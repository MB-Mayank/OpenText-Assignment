"""
Project Profile Extractor
Extracts structured project information from plain-text descriptions using LLM
"""

import json
from typing import Dict, Any
from llm_client import LLMClient


class ProfileExtractor:
    """Extracts structured project profiles from natural language descriptions"""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize profile extractor
        
        Args:
            llm_client: LLM client instance for API calls
        """
        self.llm = llm_client
        
    def extract_profile(self, description: str) -> Dict[Any, Any]:
        """
        Extract structured project profile from description
        
        Args:
            description: Plain-text project description
            
        Returns:
            Structured project profile as dictionary
        """
        system_prompt = """You are a cloud infrastructure analyst. Extract structured project information from user descriptions.

CRITICAL: Return ONLY valid JSON, no markdown formatting, no explanations, no code blocks.

Output schema:
{
  "name": "Project Name",
  "budget_inr_per_month": <number>,
  "description": "Brief summary",
  "tech_stack": {
    "frontend": "technology or null",
    "backend": "technology or null",
    "database": "technology or null",
    "proxy": "technology or null",
    "hosting": "cloud provider or null",
    "storage": "storage solution or null",
    "monitoring": "monitoring tool or null",
    "analytics": "analytics tool or null",
    "other": []
  },
  "non_functional_requirements": ["requirement1", "requirement2"]
}

Rules:
1. Extract budget in INR per month (convert if given in other currency/timeframe)
2. Identify all technologies mentioned
3. Infer common non-functional requirements (scalability, cost efficiency, reliability, etc.)
4. If information is missing, use null or empty arrays
5. Keep description concise (1-2 sentences)
6. Return pure JSON only"""

        user_prompt = f"Extract project profile from this description:\n\n{description}"
        
        print("🔍 Extracting project profile...")
        profile = self.llm.generate_json(system_prompt, user_prompt)
        print("✅ Project profile extracted successfully")
        
        return profile
    
    def save_profile(self, profile: Dict[Any, Any], output_path: str = "outputs/project_profile.json"):
        """
        Save profile to JSON file
        
        Args:
            profile: Project profile dictionary
            output_path: Path to save JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        print(f"💾 Profile saved to {output_path}")
    
    def load_profile(self, input_path: str = "outputs/project_profile.json") -> Dict[Any, Any]:
        """
        Load profile from JSON file
        
        Args:
            input_path: Path to JSON file
            
        Returns:
            Project profile dictionary
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        return profile
    
    def validate_profile(self, profile: Dict[Any, Any]) -> bool:
        """
        Validate project profile structure
        
        Args:
            profile: Project profile dictionary
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        required_fields = ["name", "budget_inr_per_month", "description", "tech_stack", "non_functional_requirements"]
        
        for field in required_fields:
            if field not in profile:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(profile["budget_inr_per_month"], (int, float)):
            raise ValueError("budget_inr_per_month must be a number")
        
        if not isinstance(profile["tech_stack"], dict):
            raise ValueError("tech_stack must be an object")
        
        if not isinstance(profile["non_functional_requirements"], list):
            raise ValueError("non_functional_requirements must be an array")
        
        print("✅ Profile validation passed")
        return True