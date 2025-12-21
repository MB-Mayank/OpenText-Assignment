"""
LLM Client for Groq API Integration
Handles all LLM API calls with retry logic and JSON parsing
"""

import os
import json
import time
from groq import Groq
from typing import Optional, Dict, Any


class LLMClient:
    """Client for interacting with Groq LLM API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (reads from env if not provided)
            model: Model to use for generation
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        
    def generate_json(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_retries: int = 3,
        temperature: float = 0.7
    ) -> Dict[Any, Any]:
        """
        Generate JSON output from LLM with retry logic
        
        Args:
            system_prompt: System instruction for the LLM
            user_prompt: User query/input
            max_retries: Number of retry attempts on failure
            temperature: Sampling temperature (0-2)
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            ValueError: If JSON parsing fails after all retries
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=4096
                )
                
                content = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                content = content.strip()
                
                # Parse JSON
                result = json.loads(content)
                return result
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed: Invalid JSON response")
                if attempt < max_retries - 1:
                    print(f"   Retrying with stricter instructions...")
                    time.sleep(1)
                    # Add stricter JSON instruction for retry
                    system_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanations, just pure JSON."
                else:
                    print(f"   Raw response: {content[:200]}...")
                    raise ValueError(f"Failed to parse JSON after {max_retries} attempts: {str(e)}")
                    
            except Exception as e:
                print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    raise
        
        raise ValueError("Failed to generate valid JSON response")
    
    def generate_text(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Generate plain text output from LLM
        
        Args:
            system_prompt: System instruction for the LLM
            user_prompt: User query/input
            temperature: Sampling temperature
            
        Returns:
            Text response from LLM
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=2048
        )
        
        return response.choices[0].message.content.strip()