from .base_converter import BaseConverter
from typing import Dict

class ControllerConverter(BaseConverter):
    def convert(self, content: str, metadata: Dict = None) -> str:
        prompt = f"""Convert this Jakarta EE Controller to its Spring Boot equivalent.
Follow these guidelines:
1. Use modern Spring Boot 3.x conventions
2. Convert JAX-RS annotations to Spring MVC
3. Use @RestController instead of @Path
4. Convert @GET, @POST, etc. to @GetMapping, @PostMapping
5. Use @PathVariable instead of @PathParam
6. Use @RequestParam instead of @QueryParam
7. Use ResponseEntity for responses
8. Maintain the same business logic
9. Include all necessary imports

Original Controller:
{content}
"""
        if metadata:
            prompt += f"\nMetadata/Context:\n{metadata}"
            
        try:
            response = self.model.generate_content(prompt)
            return self._clean_llm_response(response.text)
        except Exception as e:
            print(f"Error converting controller: {str(e)}")
            return None 