"""
Streaming Response Management

This module provides streaming response capabilities for handling
large datasets and real-time data transmission.
"""

from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict, Any, List, Optional, Callable
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


class StreamingManager:
    """Streaming Response Manager
    
    Provides utilities for streaming JSON arrays, Server-Sent Events,
    and other streaming response formats.
    """
    
    @staticmethod
    async def stream_json_array(
        items: AsyncGenerator[Dict[str, Any], None]
    ) -> StreamingResponse:
        """Stream a JSON array
        
        Args:
            items: Async generator of items to stream
            
        Returns:
            StreamingResponse for the JSON array
        """
        async def generate():
            """Generator function"""
            yield b"["
            first = True
            
            try:
                async for item in items:
                    if not first:
                        yield b","
                    yield json.dumps(item, ensure_ascii=False).encode()
                    first = False
            except Exception as e:
                logger.error(f"Error streaming JSON array: {e}")
                raise
            finally:
                yield b"]"
        
        return StreamingResponse(
            generate(),
            media_type="application/json",
            headers={
                "Cache-Control": "no-cache",
                "Transfer-Encoding": "chunked"
            }
        )
    
    @staticmethod
    async def stream_server_sent_events(
        events: AsyncGenerator[Dict[str, Any], None]
    ) -> StreamingResponse:
        """Stream Server-Sent Events (SSE)
        
        Args:
            events: Async generator of events to stream
            
        Returns:
            StreamingResponse for SSE
        """
        async def generate():
            """Generator function"""
            try:
                async for event in events:
                    # Format: data: {json}\n\n
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode()
            except Exception as e:
                logger.error(f"Error streaming SSE: {e}")
                error_event = {"error": str(e), "type": "error"}
                yield f"data: {json.dumps(error_event)}\n\n".encode()
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable Nginx buffering
            }
        )
    
    @staticmethod
    async def stream_ndjson(
        items: AsyncGenerator[Dict[str, Any], None]
    ) -> StreamingResponse:
        """Stream Newline-Delimited JSON (NDJSON)
        
        Args:
            items: Async generator of items to stream
            
        Returns:
            StreamingResponse for NDJSON
        """
        async def generate():
            """Generator function"""
            try:
                async for item in items:
                    yield json.dumps(item, ensure_ascii=False).encode()
                    yield b"\n"
            except Exception as e:
                logger.error(f"Error streaming NDJSON: {e}")
                raise
        
        return StreamingResponse(
            generate(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache"
            }
        )
    
    @staticmethod
    def create_async_generator(
        items: List[Dict[str, Any]],
        delay: float = 0.0
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Create an async generator from a list with optional delay
        
        Args:
            items: List of items to stream
            delay: Delay between items in seconds
            
        Returns:
            Async generator
        """
        async def generator():
            for item in items:
                if delay > 0:
                    await asyncio.sleep(delay)
                yield item
        
        return generator()
    
    @staticmethod
    def create_batch_generator(
        items: List[Dict[str, Any]],
        batch_size: int = 10,
        delay: float = 0.0
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Create an async generator that yields batches
        
        Args:
            items: List of items to stream
            batch_size: Number of items per batch
            delay: Delay between batches in seconds
            
        Returns:
            Async generator of batches
        """
        async def generator():
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                if delay > 0:
                    await asyncio.sleep(delay)
                yield batch
        
        return generator()
    
    @staticmethod
    async def stream_with_progress(
        items: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[float], None]] = None,
        delay: float = 0.0
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream items with progress tracking
        
        Args:
            items: List of items to stream
            progress_callback: Optional callback function for progress updates
            delay: Delay between items in seconds
            
        Returns:
            Async generator
        """
        total = len(items)
        for i, item in enumerate(items):
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Update progress
            if progress_callback:
                progress = (i + 1) / total
                try:
                    progress_callback(progress)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
            
            yield item


class StreamBuffer:
    """Buffer for streaming operations
    
    Accumulates data and flushes at specified intervals or sizes.
    """
    
    def __init__(
        self,
        flush_size: int = 1000,
        flush_interval: float = 1.0
    ):
        """Initialize stream buffer
        
        Args:
            flush_size: Number of items to buffer before flushing
            flush_interval: Time interval between flushes (seconds)
        """
        self.flush_size = flush_size
        self.flush_interval = flush_interval
        self.buffer: List[Dict[str, Any]] = []
        self.lock = asyncio.Lock()
        self.last_flush_time = 0
    
    async def add(self, item: Dict[str, Any]) -> bool:
        """Add an item to the buffer
        
        Args:
            item: Item to add
            
        Returns:
            True if buffer is ready to flush, False otherwise
        """
        async with self.lock:
            self.buffer.append(item)
            current_time = asyncio.get_event_loop().time()
            
            # Check if we should flush
            should_flush = (
                len(self.buffer) >= self.flush_size or
                (current_time - self.last_flush_time) >= self.flush_interval
            )
            
            if should_flush:
                self.last_flush_time = current_time
            
            return should_flush
    
    async def get_and_clear(self) -> List[Dict[str, Any]]:
        """Get all items and clear the buffer
        
        Returns:
            List of buffered items
        """
        async with self.lock:
            items = self.buffer.copy()
            self.buffer.clear()
            return items
    
    async def size(self) -> int:
        """Get current buffer size
        
        Returns:
            Number of items in buffer
        """
        async with self.lock:
            return len(self.buffer)
    
    async def clear(self):
        """Clear the buffer"""
        async with self.lock:
            self.buffer.clear()


class WebSocketStreamer:
    """WebSocket streaming helper
    
    Helps manage WebSocket connections for streaming data.
    """
    
    def __init__(
        self,
        websocket,
        heartbeat_interval: float = 30.0
    ):
        """Initialize WebSocket streamer
        
        Args:
            websocket: WebSocket connection
            heartbeat_interval: Heartbeat ping interval in seconds
        """
        self.websocket = websocket
        self.heartbeat_interval = heartbeat_interval
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the streamer"""
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("WebSocket streamer started")
    
    async def stop(self):
        """Stop the streamer"""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        logger.info("WebSocket streamer stopped")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                if self._running:
                    await self.websocket.send_json({"type": "heartbeat"})
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                break
    
    async def send(self, data: Dict[str, Any]):
        """Send data over WebSocket
        
        Args:
            data: Data to send
        """
        if self._running:
            await self.websocket.send_json(data)
    
    async def send_event(self, event_type: str, data: Any):
        """Send an event over WebSocket
        
        Args:
            event_type: Type of event
            data: Event data
        """
        await self.send({
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def send_error(self, error: str):
        """Send an error over WebSocket
        
        Args:
            error: Error message
        """
        await self.send({
            "type": "error",
            "error": error,
            "timestamp": asyncio.get_event_loop().time()
        })


__all__ = [
    "StreamingManager",
    "StreamBuffer",
    "WebSocketStreamer",
]
