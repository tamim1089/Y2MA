"""
LLM Provider Module
Wraps Ollama API for text generation
"""

import os
import time
from typing import Iterator, Optional, Dict, Any
import logging
import requests

logger = logging.getLogger(__name__)


class OllamaProvider:
    """
    LLM provider wrapping Ollama's REST API.
    """
    
    def __init__(
        self,
        base_url: str = None,
        model_name: str = None
    ):
        """
        Initialize the Ollama provider.
        
        Args:
            base_url: Ollama API base URL
            model_name: Name of the model to use
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://38.39.92.215:443')
        self.model_name = model_name or os.getenv('OLLAMA_MODEL', 'llama3.1:8b-instruct-fp16')
        
        # API endpoints
        self.generate_url = f"{self.base_url}/api/generate"
        self.chat_url = f"{self.base_url}/api/chat"
        
        # Retry settings
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # Exponential backoff
        
        # Timeouts
        self.connect_timeout = 30
        self.read_timeout = 120
        
        logger.info(f"OllamaProvider initialized: {self.base_url} / {self.model_name}")
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 512,
        system: str = None,
        **kwargs
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            system: Optional system prompt
            **kwargs: Additional Ollama parameters
        
        Returns:
            Generated text
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs.get('options', {})
            }
        }
        
        if system:
            payload["system"] = system
        
        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.generate_url,
                    json=payload,
                    timeout=(self.connect_timeout, self.read_timeout)
                )
                response.raise_for_status()
                
                result = response.json()
                generated_text = result.get('response', '')
                
                logger.info(f"Generated {len(generated_text)} chars")
                return generated_text
                
            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")
            
            # Wait before retry
            if attempt < self.max_retries - 1:
                delay = self.retry_delays[attempt]
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
        
        # All retries failed
        logger.error(f"All {self.max_retries} attempts failed: {last_error}")
        raise ConnectionError(f"Failed to generate after {self.max_retries} attempts: {last_error}")
    
    def stream(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 512,
        system: str = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream text completion token by token.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: Optional system prompt
            **kwargs: Additional Ollama parameters
        
        Yields:
            Generated text chunks
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs.get('options', {})
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                stream=True,
                timeout=(self.connect_timeout, self.read_timeout)
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    import json
                    chunk = json.loads(line)
                    text = chunk.get('response', '')
                    if text:
                        yield text
                    
                    # Check if done
                    if chunk.get('done', False):
                        break
                        
        except requests.exceptions.RequestException as e:
            logger.error(f"Streaming error: {e}")
            raise ConnectionError(f"Streaming failed: {e}")
    
    def chat(
        self,
        messages: list,
        temperature: float = 0.3,
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """
        Chat completion with message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Assistant's response
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs.get('options', {})
            }
        }
        
        try:
            response = requests.post(
                self.chat_url,
                json=payload,
                timeout=(self.connect_timeout, self.read_timeout)
            )
            response.raise_for_status()
            
            result = response.json()
            message = result.get('message', {})
            content = message.get('content', '')
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat error: {e}")
            raise ConnectionError(f"Chat failed: {e}")
    
    def count_tokens(self, text: str) -> int:
        """
        Approximate token count.
        Uses character-based estimation (~4 chars per token).
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Approximate token count
        """
        return len(text) // 4
    
    def is_available(self) -> bool:
        """Check if the Ollama server is available"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """List available models"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return [m.get('name') for m in data.get('models', [])]
        except:
            return []


if __name__ == "__main__":
    # Test the LLM provider
    logging.basicConfig(level=logging.INFO)
    
    print("Testing OllamaProvider...")
    
    provider = OllamaProvider()
    
    # Check availability
    print(f"\nServer available: {provider.is_available()}")
    
    models = provider.list_models()
    print(f"Available models: {models[:5]}...")
    
    # Test generation
    print("\nTesting generation...")
    try:
        response = provider.generate(
            "Say hello in one sentence.",
            temperature=0.3,
            max_tokens=50
        )
        print(f"Response: {response}")
        print("\n✅ LLM provider test passed!")
    except Exception as e:
        print(f"❌ Error: {e}")
