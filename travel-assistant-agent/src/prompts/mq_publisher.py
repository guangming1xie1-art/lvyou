"""消息队列发布者模块

提供RabbitMQ消息发布功能，用于通知所有Agent节点更新提示词。
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptMQPublisher:
    """提示词消息队列发布者
    
    发布提示词更新消息到RabbitMQ，通知所有订阅的Agent节点。
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        exchange: str = "prompt_updates",
        virtual_host: str = "/"
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange
        self.virtual_host = virtual_host
        
        self.connection = None
        self.channel = None
        
    async def connect(self) -> bool:
        """连接到RabbitMQ服务器
        
        Returns:
            是否连接成功
        """
        try:
            import aio_pika
            
            url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.virtual_host}"
            
            self.connection = await aio_pika.connect_robust(url)
            self.channel = await self.connection.channel()
            
            await self.channel.declare_exchange(
                self.exchange,
                aio_pika.ExchangeType.FANOUT,
                durable=True
            )
            
            logger.info(f"Publisher connected to RabbitMQ at {self.host}:{self.port}")
            return True
            
        except ImportError:
            logger.warning("aio_pika not installed, MQ publisher disabled")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
            
    async def disconnect(self):
        """断开与RabbitMQ的连接"""
        if self.connection:
            try:
                await self.connection.close()
                logger.info("Publisher disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
            finally:
                self.connection = None
                self.channel = None
                
    async def publish_prompt_update(
        self,
        update_type: str,
        category: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        updated_by: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """发布提示词更新消息
        
        Args:
            update_type: 更新类型 (create/update/delete/reload_all)
            category: 提示词分类
            name: 提示词名称
            version: 提示词版本
            updated_by: 更新者
            extra_data: 额外数据
            
        Returns:
            是否发布成功
        """
        if not self.channel:
            connected = await self.connect()
            if not connected:
                return False
                
        try:
            import aio_pika
            
            message_data = {
                "type": update_type,
                "category": category,
                "name": name,
                "version": version,
                "updated_by": updated_by,
                "timestamp": datetime.utcnow().isoformat(),
                "extra": extra_data or {}
            }
            
            message_body = json.dumps(message_data, ensure_ascii=False)
            
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body.encode('utf-8'),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=self.exchange
            )
            
            logger.info(f"Published prompt update message: {update_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
            
    async def publish_reload_all(self, reason: str = "manual_trigger") -> bool:
        """发布全量重新加载消息
        
        Args:
            reason: 触发原因
            
        Returns:
            是否发布成功
        """
        return await self.publish_prompt_update(
            update_type="reload_all",
            extra_data={"reason": reason}
        )
        
    async def publish_prompt_created(
        self,
        category: str,
        name: str,
        version: str,
        updated_by: Optional[str] = None
    ) -> bool:
        """发布提示词创建消息
        
        Args:
            category: 提示词分类
            name: 提示词名称
            version: 提示词版本
            updated_by: 创建者
            
        Returns:
            是否发布成功
        """
        return await self.publish_prompt_update(
            update_type="create",
            category=category,
            name=name,
            version=version,
            updated_by=updated_by
        )
        
    async def publish_prompt_updated(
        self,
        category: str,
        name: str,
        version: str,
        updated_by: Optional[str] = None
    ) -> bool:
        """发布提示词更新消息
        
        Args:
            category: 提示词分类
            name: 提示词名称
            version: 提示词版本
            updated_by: 更新者
            
        Returns:
            是否发布成功
        """
        return await self.publish_prompt_update(
            update_type="update",
            category=category,
            name=name,
            version=version,
            updated_by=updated_by
        )
        
    async def publish_prompt_deleted(
        self,
        category: str,
        name: str,
        updated_by: Optional[str] = None
    ) -> bool:
        """发布提示词删除消息
        
        Args:
            category: 提示词分类
            name: 提示词名称
            updated_by: 删除者
            
        Returns:
            是否发布成功
        """
        return await self.publish_prompt_update(
            update_type="delete",
            category=category,
            name=name,
            updated_by=updated_by
        )
        
    def get_status(self) -> Dict[str, Any]:
        """获取发布者状态
        
        Returns:
            状态信息字典
        """
        return {
            "host": self.host,
            "port": self.port,
            "exchange": self.exchange,
            "is_connected": self.connection is not None and not self.connection.is_closed
        }


prompt_mq_publisher = PromptMQPublisher()
