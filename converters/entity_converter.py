from .base_converter import BaseConverter
from typing import Dict

class EntityConverter(BaseConverter):
    def convert(self, content: str, metadata: Dict = None) -> str:
        prompt = f"""Convert this JPA Entity to its Spring Boot MongoDB equivalent.
Follow these guidelines:
1. Convert JPA annotations to Spring Data MongoDB
2. Replace @Entity with @Document
3. Replace @Column with @Field
4. Keep @Id but update import
5. Use appropriate MongoDB mapping annotations
6. Include all necessary imports

Original Entity:
{content}
"""
        if metadata:
            prompt += f"\nMetadata/Context:\n{metadata}"
            
        try:
            response = self.model.generate_content(prompt)
            return self._clean_llm_response(response.text)
        except Exception as e:
            print(f"Error converting entity: {str(e)}")
            return None 