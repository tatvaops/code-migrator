import os
from typing import Dict
import google.generativeai as genai

class BaseConverter:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def convert(self, content: str, metadata: Dict = None) -> str:
        """Base convert method to be implemented by specific converters"""
        raise NotImplementedError
        
    def _clean_llm_response(self, response: str) -> str:
        """Clean the LLM response by removing markdown code block markers"""
        response = response.strip()
        if response.startswith("```") and response.endswith("```"):
            response = response.split('\n', 1)[1]
            response = response.rsplit('\n', 1)[0]
        return response.strip() 