from .base_converter import BaseConverter
from typing import Dict

class RepositoryConverter(BaseConverter):
    def convert(self, content: str, metadata: Dict = None) -> str:
        prompt = f"""Convert this Jakarta EE Repository to its Spring Boot equivalent.
Follow these guidelines:
1. Convert to Spring Data interface
2. Extend appropriate Spring Data repository interface
3. Convert JPQL/HQL queries to Spring Data queries
4. Use Spring Data MongoDB annotations
5. Maintain the same business logic
6. Include all necessary imports

Original Repository:
{content}
"""
        if metadata:
            prompt += f"\nMetadata/Context:\n{metadata}"
            
        try:
            response = self.model.generate_content(prompt)
            return self._clean_llm_response(response.text)
        except Exception as e:
            print(f"Error converting repository: {str(e)}")
            return None 