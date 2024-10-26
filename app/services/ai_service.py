import json
import os
import logging
import asyncio
from typing import Dict, Tuple, Any, List
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
        self.functions: Dict[str, Dict[str, Any]] = {}
        self._load_all_prompts()
        logger.info(f"AIService initialized with model: {self.model}")


    def _load_all_prompts(self):
        """Load all prompts and their functions from the prompts directory"""

        # Iterate over all prompt directories
        for prompt_dir in os.listdir(self.prompts_dir):
            prompt_path = os.path.join(self.prompts_dir, prompt_dir)
            if os.path.isdir(prompt_path):
                try:

                    # Load prompt configuration
                    with open(os.path.join(prompt_path, 'prompt.json'), 'r') as f:
                        self.prompts[prompt_dir] = json.load(f)

                    # Load function
                    with open(os.path.join(prompt_path, 'function.json'), 'r') as f:
                        function_data = json.load(f)

                        # Use first function function if it's an array
                        self.functions[prompt_dir] = (
                            function_data[0] if isinstance(function_data, list)
                            else function_data
                        )

                    # Log the loaded prompt and function
                    logger.info(f"Loaded prompt and function for: {prompt_dir}")

                except Exception as e:
                    logger.error(f"Error loading prompt {prompt_dir}: {str(e)}")


    def _get_prompt(self, prompt_name: str, message: str) -> Tuple[str, str]:
        """Get the system and user prompts for a given prompt name"""

        # Check if the prompt exists
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt not found: {prompt_name}")
        
        # Get the prompt configuration
        prompt_config = self.prompts[prompt_name]
        system_prompt = prompt_config['system']
        user_prompt = prompt_config['user'].format(message=message)
        
        # Return the system and user prompts
        return system_prompt, user_prompt


    def _get_function(self, prompt_name: str) -> List[Dict[str, Any]]:
        """Get the function for a given prompt name"""

        # Get the function
        if prompt_name not in self.functions:
            raise ValueError(f"function not found: {prompt_name}")

        # Get the function
        function = self.functions[prompt_name]

        # Return as a list with proper function structure
        return [{
            "name": function["name"],
            "description": function["description"],
            "parameters": function["parameters"]
        }]


    async def process_messages(self, prompt_name: str):
        while True:
            try:
                # Check if the input queue is too large
                input_size = self.input_queue.qsize()
                if input_size > 10:  # arbitrary threshold
                    logger.warning(f"Input queue size is high: {input_size}")

                # Wait for a message in the input queue
                logger.debug("AIService: Waiting for message in input queue...")
                async with asyncio.timeout(30):  # 30-second timeout
                    chat_id, message = await self.input_queue.get()

                # Process the message
                logger.info(f"AIService: Processing message for chat {chat_id}")
                response = await self.process_gpt(prompt_name, message)
                logger.info(f"AIService: Generated response for chat {chat_id}")

                # Convert response to JSON if it's a dictionary
                if isinstance(response, dict):
                    response = json.dumps(response, ensure_ascii=False)

                # Add the response to the response queue
                await self.response_queue.put((chat_id, response))
                logger.info(f"AIService: Response added to response queue for chat {chat_id}")

                # Mark the message as processed
                self.input_queue.task_done()

            except asyncio.TimeoutError:
                logger.debug("No messages received in the last 30 seconds")

            except Exception as e:
                logger.error(f"AIService: Error processing message: {str(e)}", exc_info=True)


    async def process_gpt(self, prompt_name: str, message: str) -> str:
        try:

            # Get the system and user prompts
            system_prompt, user_prompt = self._get_prompt(prompt_name, message)
            
            # Create the messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Get the function function
            function = self._get_function(prompt_name)

            # Send the request to OpenAI API
            logger.debug(f"Sending request to OpenAI API for prompt: {prompt_name}")
            chat_completion = await self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                functions=function,
                function_call="auto"
            )

            # Get the response
            logger.debug(f"Received response from OpenAI API for prompt: {prompt_name}")
            response = chat_completion.choices[0].message

            # Process the response
            if response.function_call:
                logger.debug("Processing function call response")
                return json.dumps(json.loads(response.function_call.arguments))
            else:
                logger.debug("Processing text response")
                return response.content.strip()

        except Exception as e:
            logger.error(f"Error processing message with OpenAI: {str(e)}")
            raise
