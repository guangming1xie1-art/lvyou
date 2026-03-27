import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageMQPublisher:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        queue: str = "message.queue",
        virtual_host: str = "/"
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue = queue
        self.virtual_host = virtual_host
        
        self.connection = None
        self.channel = None
        
    async def connect(self) -> bool:
        try:
            import aio_pika
            
            url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.virtual_host}"
            
            self.connection = await aio_pika.connect_robust(url)
            self.channel = await self.connection.channel()
            
            await self.channel.declare_queue(
                self.queue,
                durable=True
            )
            
            logger.info(f"Message publisher connected to RabbitMQ at {self.host}:{self.port}")
            return True
            
        except ImportError:
            logger.warning("aio_pika not installed, MQ publisher disabled")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
            
    async def disconnect(self):
        if self.connection:
            try:
                await self.connection.close()
                logger.info("Message publisher disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
            finally:
                self.connection = None
                self.channel = None
                
    async def publish_message(
        self,
        session_id: str,
        user_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        if not self.channel:
            connected = await self.connect()
            if not connected:
                return False
                
        try:
            import aio_pika
            
            message_data = {
                "session_id": session_id,
                "user_id": user_id,
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            message_body = json.dumps(message_data, ensure_ascii=False)
            
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body.encode('utf-8'),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=self.queue
            )
            
            logger.debug(f"Published message for session: {session_id}, role: {role}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False


message_mq_publisher = MessageMQPublisher()
