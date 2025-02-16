from .base_converter import BaseConverter
from typing import Dict
import os
from utils.namespace_handler import get_package_declaration

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
7. Use Lombok annotations:
   - @Getter @Setter instead of explicit getters and setters
   - @NoArgsConstructor for default constructor
   - @AllArgsConstructor for all-args constructor
   - @Builder for builder pattern
   - @Data if appropriate (combines @Getter @Setter @ToString @EqualsAndHashCode)
8. Follow camelCase naming convention for:
   - File names (e.g., memberEntity.java)
   - Field names
   - Method names
9. Add appropriate documentation
10. Package should be {get_package_declaration('Entity')}

Original Entity:
{content}
"""
        if metadata:
            prompt += f"\nMetadata/Context:\n{metadata}"
            
        try:
            response = self.model.generate_content(prompt)
            converted_content = self._clean_llm_response(response.text)
            
            # Ensure the converted content includes Lombok imports
            if "@Getter" in converted_content and "import lombok" not in converted_content:
                converted_content = "import lombok.*;\n\n" + converted_content
            
            return converted_content
        except Exception as e:
            print(f"Error converting entity: {str(e)}")
            return None
    
    def get_converted_filename(self, original_filename: str) -> str:
        """Convert filename to camelCase"""
        # Remove .java extension
        name = os.path.splitext(original_filename)[0]
        
        # Handle common suffixes
        for suffix in ['Entity', 'Model', 'Document']:
            if name.endswith(suffix):
                base = name[:-len(suffix)]
                # Convert first character to lowercase
                return f"{base[0].lower()}{base[1:]}{suffix}.java"
        
        # If no known suffix, just convert first character to lowercase
        return f"{name[0].lower()}{name[1:]}.java" 