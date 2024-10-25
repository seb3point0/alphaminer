import json
import os
import logging
import asyncio
from typing import Dict, Tuple, Any
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, input_queue: asyncio.Queue, response_queue: asyncio.Queue):
        self.input_queue = input_queue
        self.response_queue = response_queue
        self.client = AsyncOpenAI(api_key=settings.OPENAI_TOKEN)
        self.model = settings.OPENAI_MODEL
        self.prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self._load_all_prompts()
        logger.info(f"AIService initialized with model: {self.model}")

    def _load_all_prompts(self):
        """Load all prompts and their schemas from the prompts directory"""
        for prompt_dir in os.listdir(self.prompts_dir):
            prompt_path = os.path.join(self.prompts_dir, prompt_dir)
            if os.path.isdir(prompt_path):
                try:
                    # Load prompt configuration
                    with open(os.path.join(prompt_path, 'prompt.json'), 'r') as f:
                        self.prompts[prompt_dir] = json.load(f)
                    # Load schema
                    with open(os.path.join(prompt_path, 'schema.json'), 'r') as f:
                        self.schemas[prompt_dir] = json.load(f)
                    logger.info(f"Loaded prompt and schema for: {prompt_dir}")
                except Exception as e:
                    logger.error(f"Error loading prompt {prompt_dir}: {str(e)}")

    def _get_prompt(self, prompt_name: str, message: str) -> Tuple[str, str]:
        """Get the system and user prompts for a given prompt name"""
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt not found: {prompt_name}")
        
        prompt_config = self.prompts[prompt_name]
        system_prompt = prompt_config['system_prompt']
        user_prompt = prompt_config['user_prompt_template'].format(message=message)
        
        return system_prompt, user_prompt

    def _get_schema(self, prompt_name: str) -> Dict[str, Any]:
        """Get the schema for a given prompt name"""
        if prompt_name not in self.schemas:
            raise ValueError(f"Schema not found: {prompt_name}")
        return self.schemas[prompt_name]

    async def process_messages(self, prompt_name: str):
        while True:
            try:
                input_size = self.input_queue.qsize()
                if input_size > 10:  # arbitrary threshold
                    logger.warning(f"Input queue size is high: {input_size}")
                logger.debug("AIService: Waiting for message in input queue...")
                async with asyncio.timeout(30):  # 30-second timeout
                    chat_id, message = await self.input_queue.get()
                logger.info(f"AIService: Processing message for chat {chat_id}")
                
                response = await self.process_gpt(prompt_name, message)
                logger.info(f"AIService: Generated response for chat {chat_id}")
                
                if isinstance(response, dict):
                    response = json.dumps(response, ensure_ascii=False)
                
                await self.response_queue.put((chat_id, response))
                logger.info(f"AIService: Response added to response queue for chat {chat_id}")
                self.input_queue.task_done()
            except asyncio.TimeoutError:
                logger.debug("No messages received in the last 30 seconds")
            except Exception as e:
                logger.error(f"AIService: Error processing message: {str(e)}", exc_info=True)

    async def process_gpt(self, prompt_name: str, message: str) -> str:
        try:
            system_prompt, user_prompt = self._get_prompt(prompt_name, message)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            function_schema = self._get_schema(prompt_name)

            logger.debug(f"Sending request to OpenAI API for prompt: {prompt_name}")
            chat_completion = await self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                functions=function_schema,
                function_call="auto"
            )

            logger.debug(f"Received response from OpenAI API for prompt: {prompt_name}")
            response = chat_completion.choices[0].message

            if response.function_call:
                logger.debug("Processing function call response")
                return json.dumps(json.loads(response.function_call.arguments))
            else:
                logger.debug("Processing text response")
                return response.content.strip()

        except Exception as e:
            logger.error(f"Error processing message with OpenAI: {str(e)}")
            raise
