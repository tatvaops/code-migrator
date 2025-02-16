from .base_converter import BaseConverter
from typing import Dict

class ViewConverter(BaseConverter):
    def convert(self, content: str, metadata: Dict = None) -> str:
        prompt = f"""Convert this JSF/XHTML view to its Spring Boot Thymeleaf equivalent.
Follow these guidelines:
1. Convert JSF/XHTML to Thymeleaf template
2. Replace JSF tags with Thymeleaf attributes
3. Update form handling
4. Update resource references
5. Use Thymeleaf layout system

Original View:
{content}
"""
        if metadata:
            prompt += f"\nMetadata/Context:\n{metadata}"
            
        try:
            response = self.model.generate_content(prompt)
            return self._clean_llm_response(response.text)
        except Exception as e:
            print(f"Error converting view: {str(e)}")
            return None 