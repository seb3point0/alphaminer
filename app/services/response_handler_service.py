import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ResponseHandlerService:
    def __init__(self, response_queue: asyncio.Queue, telegram_service):
        self.response_queue = response_queue
        self.telegram_service = telegram_service
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the response handler service"""
        logger.info("Starting ResponseHandlerService")
        self.task = asyncio.create_task(self._process_responses())
        return self.task

    async def stop(self):
        """Stop the response handler service"""
        if self.task:
            logger.info("Stopping ResponseHandlerService")
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info("ResponseHandlerService stopped")

    async def _process_responses(self):
        """Process responses from the queue"""
        logger.info("Starting to process responses")
        while True:
            try:
                logger.debug(f"Waiting for response in queue (size: {self.response_queue.qsize()})...")
                chat_id, response = await self.response_queue.get()
                
                try:
                    await self._handle_response(chat_id, response)
                except Exception as e:
                    logger.error(f"Error handling response for chat {chat_id}: {str(e)}", exc_info=True)
                finally:
                    self.response_queue.task_done()
                    
            except asyncio.CancelledError:
                logger.info("Response processing cancelled")
                break
            except Exception as e:
                logger.error(f"Error in response processing loop: {str(e)}", exc_info=True)

    async def _handle_response(self, chat_id: int, response: str):
        """Handle a single response"""
        logger.info(f"Handling response for chat {chat_id}")
        # Here you can add different response handling logic based on response type
        await self.telegram_service.send_response(chat_id, response)
        logger.info(f"Response handled for chat {chat_id}")
