"""消息队列消费者模块

监听RabbitMQ消息，实现分布式环境下的提示词热更新。
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptMQConsumer:
    """提示词消息队列消费者
    
    监听RabbitMQ队列，接收提示词更新消息并触发重新加载。
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        exchange: str = "prompt_updates",
        queue_name: str = "prompt_update_queue",
        virtual_host: str = "/"
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange
        self.queue_name = queue_name
        self.virtual_host = virtual_host
        
        self.connection = None
        self.channel = None
        self.is_running = False
        self._on_message_callback: Optional[Callable] = None
        
    def set_message_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """设置消息处理回调函数
        
        Args:
            callback: 消息处理回调函数，接收消息字典作为参数
        """
        self._on_message_callback = callback
        
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
            
            queue = await self.channel.declare_queue(
                self.queue_name,
                durable=True,
                auto_delete=False
            )
            
            await queue.bind(self.exchange)
            
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True
            
        except ImportError:
            logger.warning("aio_pika not installed, MQ consumer disabled")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
            
    async def disconnect(self):
        """断开与RabbitMQ的连接"""
        if self.connection:
            try:
                await self.connection.close()
                logger.info("Disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
            finally:
                self.connection = None
                self.channel = None
                
    async def start_consuming(self):
        """开始消费消息"""
        if not self.channel:
            logger.error("Not connected to RabbitMQ")
            return
            
        try:
            import aio_pika
            
            queue = await self.channel.get_queue(self.queue_name)
            
            async with queue.iterator() as queue_iter:
                self.is_running = True
                logger.info("Started consuming prompt update messages...")
                
                async for message in queue_iter:
                    if not self.is_running:
                        break
                        
                    async with message.process():
                        await self._process_message(message)
                        
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            self.is_running = False
            
    def stop_consuming(self):
        """停止消费消息"""
        self.is_running = False
        logger.info("Stopped consuming messages")
        
    async def _process_message(self, message):
        """处理接收到的消息
        
        Args:
            message: RabbitMQ消息对象
        """
        try:
            body = message.body.decode('utf-8')
            data = json.loads(body)
            
            logger.info(f"Received prompt update message: {data.get('type', 'unknown')}")
            
            if self._on_message_callback:
                await self._on_message_callback(data)
            else:
                logger.warning("No message callback set, message ignored")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    async def run_forever(self):
        """持续运行消费者"""
        while self.is_running:
            try:
                if not self.connection or self.connection.is_closed:
                    connected = await self.connect()
                    if not connected:
                        await asyncio.sleep(5)
                        continue
                        
                await self.start_consuming()
                
            except Exception as e:
                logger.error(f"Consumer error: {e}")
                await asyncio.sleep(5)
                
    def get_status(self) -> Dict[str, Any]:
        """获取消费者状态
        
        Returns:
            状态信息字典
        """
        return {
            "host": self.host,
            "port": self.port,
            "exchange": self.exchange,
            "queue_name": self.queue_name,
            "is_connected": self.connection is not None and not self.connection.is_closed,
            "is_running": self.is_running
        }


prompt_mq_consumer = PromptMQConsumer()
