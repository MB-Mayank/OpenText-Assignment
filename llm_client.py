import os
import json
import time
from groq import Groq
from typing import Optional, Dict, Any


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
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
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                content = content.strip()
                result = json.loads(content)
                return result
                
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: Invalid JSON response")
                if attempt < max_retries - 1:
                    print("   Retrying with stricter instructions...")
                    time.sleep(1)
                    system_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanations, just pure JSON."
                else:
                    print(f"   Raw response: {content[:200]}...")
                    raise ValueError(f"Failed to parse JSON after {max_retries} attempts: {str(e)}")
                    
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
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