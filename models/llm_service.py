"""
LLMService: Modernized LLM calling interface using google-genai.
"""
import os
import logging
import time
from typing import Any

from google import genai

from .utils import LoggingUtils, ErrorUtils

logger = LoggingUtils.setup_logger(__name__)

class LLMService:
    """
    A simplified LLM service that uses a dependency-injected genai.Client
    to interact with the Google Generative AI API.
    """
    def __init__(self, client: genai.Client, model_name: str = "models/gemini-2.5-flash", retry_count: int = 3, retry_delay: float = 1.0):
        """
        Initializes the LLMService with a shared API client.

        Args:
            client (genai.Client): The shared google.genai.Client instance.
            model_name (str): The name of the model to use for generation.
            retry_count (int): The number of retries for an API call.
            retry_delay (float): The initial delay between retries.
        """
        self.client = client
        self.model_name = model_name
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        logger.info(f"LLMService initialized for model: {self.model_name}")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generates text using the configured model via the shared client.

        Args:
            prompt (str): The text prompt to send to the model.
            **kwargs: Additional generation parameters like 'temperature'.

        Returns:
            str: The generated text content.
        """
        attempt = 0
        last_error = None
        
        # Get generation parameters from kwargs
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 4096) # Note: Not directly used in client.models.generate_content

        while attempt < self.retry_count:
            try:
                logger.debug(f"Sending prompt to model {self.model_name} (Attempt {attempt + 1})")
                
                # The API is rejecting all optional parameters.
                # Calling with only the mandatory arguments to see if the call succeeds.
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt]
                )
                
                if response.text:
                    return response.text.strip()
                
                # Handle cases where response is empty but not an exception
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                raise ValueError(f"Model returned an empty response. Finish Reason: {finish_reason}")

            except Exception as e:
                last_error = e
                attempt += 1
                logger.warning(f"Attempt {attempt}/{self.retry_count} failed: {e}")
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay * (2 ** (attempt - 1)))

        logger.error(f"LLM generation failed after {self.retry_count} attempts: {last_error}")
        raise last_error