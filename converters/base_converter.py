import os
from typing import Dict
import google.generativeai as genai
from utils.namespace_handler import get_package_declaration

class BaseConverter:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def convert(self, content: str, metadata: Dict = None) -> str:
        """Base convert method to be implemented by specific converters"""
        raise NotImplementedError
        
    def _clean_llm_response(self, response: str) -> str:
        """Clean the LLM response and add package declaration"""
        response = response.strip()
        if response.startswith("```") and response.endswith("```"):
            response = response.split('\n', 1)[1]
            response = response.rsplit('\n', 1)[0]
        
        # Get file type from class name
        file_type = self.__class__.__name__.replace('Converter', '')
        
        # Add package declaration if it's missing
        if not response.strip().startswith("package"):
            package_decl = get_package_declaration(file_type)
            response = f"{package_decl}\n\n{response}"
            
        return response.strip() 