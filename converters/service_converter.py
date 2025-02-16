from .base_converter import BaseConverter
from typing import Dict

class ServiceConverter(BaseConverter):
    def convert(self, content: str, metadata: Dict = None) -> str:
        prompt = f"""Convert this Jakarta EE Service to its Spring Boot equivalent.
Follow these guidelines:
1. Use modern Spring Boot 3.x conventions
2. Convert @Stateless/@Stateful to @Service
3. Replace @EJB with @Autowired
4. Use Spring's @Transactional
5. Update exception handling to Spring conventions
6. Maintain the same business logic
7. Include all necessary imports

Original Service:
{content}
"""
        if metadata:
            prompt += f"\nMetadata/Context:\n{metadata}"
            
        try:
            response = self.model.generate_content(prompt)
            return self._clean_llm_response(response.text)
        except Exception as e:
            print(f"Error converting service: {str(e)}")
            return None 