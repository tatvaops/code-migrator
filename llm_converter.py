import os
import google.generativeai as genai
from typing import Dict, List
import shutil
import re

class LLMConverter:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def convert_to_spring_boot(self, file_content: str, file_type: str, metadata: Dict = None) -> str:
        """Convert Jakarta EE file to Spring Boot using Gemini"""
        
        # Construct the prompt based on file type
        prompt = self._construct_prompt(file_content, file_type, metadata)
        
        try:
            response = self.model.generate_content(prompt)
            # Clean the response by removing markdown code block markers
            cleaned_response = self._clean_llm_response(response.text)
            return cleaned_response
        except Exception as e:
            print(f"Error during conversion: {str(e)}")
            return None

    def _construct_prompt(self, file_content: str, file_type: str, metadata: Dict = None) -> str:
        """Construct appropriate prompt based on component type"""
        
        base_prompt = f"""Convert this Jakarta EE {file_type} to its Spring Boot equivalent.
Follow these guidelines:
1. Use modern Spring Boot 3.x conventions
2. Use appropriate Spring Boot annotations
3. Maintain the same business logic
4. Use Spring Boot best practices
5. Include all necessary imports
6. Maintain method signatures where possible
7. Add appropriate documentation

Original {file_type}:
{file_content}

Additional Context:
"""

        if file_type == "Controller":
            base_prompt += """
- Convert JAX-RS annotations to Spring MVC
- Use @RestController instead of @Path
- Convert @GET, @POST, etc. to @GetMapping, @PostMapping
- Use @PathVariable instead of @PathParam
- Use @RequestParam instead of @QueryParam
- Use ResponseEntity for responses
"""

        elif file_type == "Service":
            base_prompt += """
- Convert @Stateless/@Stateful to @Service
- Replace @EJB with @Autowired
- Use Spring's @Transactional
- Update exception handling to Spring conventions
"""

        elif file_type == "Repository":
            base_prompt += """
- Convert to Spring Data interface
- Extend appropriate Spring Data repository interface
- Convert JPQL/HQL queries to Spring Data queries
- Use Spring Data MongoDB annotations
"""

        elif file_type == "Entity":
            base_prompt += """
- Convert JPA annotations to Spring Data MongoDB
- Replace @Entity with @Document
- Replace @Column with @Field
- Keep @Id but update import
- Use appropriate MongoDB mapping annotations
"""

        elif file_type == "View":
            base_prompt += """
- Convert JSF/XHTML to Thymeleaf template
- Replace JSF tags with Thymeleaf attributes
- Update form handling
- Update resource references
- Use Thymeleaf layout system
"""

        if metadata:
            base_prompt += f"\nMetadata/Context:\n{metadata}"

        base_prompt += "\n\nProvide the complete Spring Boot code:"
        
        return base_prompt

    def _clean_llm_response(self, response: str) -> str:
        """Clean the LLM response by removing markdown code block markers"""
        # Remove code block markers if they exist
        response = response.strip()
        if response.startswith("```") and response.endswith("```"):
            # Remove first line (```java or similar)
            response = response.split('\n', 1)[1]
            # Remove last line (```)
            response = response.rsplit('\n', 1)[0]
        return response.strip()

def convert_path(path: str) -> str:
    """Convert file path to Spring Boot structure"""
    # Handle static resources (CSS, JS, images)
    if path.lower().endswith(('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot')):
        return os.path.join('src/main/resources/static', path.replace('webapp/', ''))
    
    # Convert XHTML/JSF to HTML
    if path.endswith(('.xhtml', '.jsf')):
        path = os.path.splitext(path)[0] + '.html'
        return os.path.join('src/main/resources/templates', path.replace('webapp/', ''))
    
    # Keep Java files in their structure
    return path

def copy_static_resources(source_dir: str, target_dir: str) -> Dict[str, int]:
    """Copy static resources and return statistics"""
    stats = {
        'copied': 0,
        'failed': 0
    }
    
    static_extensions = {
        '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', 
        '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot'
    }
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in static_extensions):
                source_path = os.path.join(root, file)
                rel_path = os.path.relpath(source_path, source_dir)
                target_path = os.path.join(target_dir, convert_path(rel_path))
                
                try:
                    # Create target directory if it doesn't exist
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(source_path, target_path)
                    stats['copied'] += 1
                    print(f"📁 Copied static resource: {rel_path}")
                except Exception as e:
                    stats['failed'] += 1
                    print(f"❌ Failed to copy {rel_path}: {str(e)}")
    
    return stats

def update_resource_references(content: str) -> str:
    """Update resource references in HTML files to match Spring Boot structure"""
    # Update CSS references
    content = re.sub(
        r'href="(/.*?\.css)"',
        r'href="@{/\1}"',
        content
    )
    
    # Update JavaScript references
    content = re.sub(
        r'src="(/.*?\.js)"',
        r'src="@{/\1}"',
        content
    )
    
    # Update image references
    content = re.sub(
        r'src="(/.*?\.(jpg|jpeg|png|gif|svg))"',
        r'src="@{/\1}"',
        content
    )
    
    return content

def convert_project(source_dir: str, target_dir: str, api_key: str):
    """Convert entire project from Jakarta EE to Spring Boot"""
    
    converter = LLMConverter(api_key)
    print(f"\n🚀 Starting project conversion:")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}\n")
    
    # Track conversion statistics
    stats = {
        "converted": 0,
        "failed": 0,
        "skipped": 0,
        "static_resources": {"copied": 0, "failed": 0}
    }
    
    # Create target directory structure
    os.makedirs(target_dir, exist_ok=True)
    
    # First, copy all static resources
    print("\n📦 Copying static resources...")
    resource_stats = copy_static_resources(source_dir, target_dir)
    stats["static_resources"] = resource_stats
    
    # Then process all files
    for root, _, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            rel_path = os.path.relpath(source_path, source_dir)
            
            # Skip if it's a static resource
            if any(file.lower().endswith(ext) for ext in ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']):
                continue
                
            print(f"\n📝 Processing: {rel_path}")
            
            # Determine file type and whether it needs conversion
            file_type = determine_file_type(source_path)
            if not file_type:
                print(f"⏭️  Skipping: {rel_path} (Unsupported file type)")
                stats["skipped"] += 1
                continue
                
            print(f"🔍 Detected file type: {file_type}")
            
            try:
                # Read source file
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get metadata from Neo4j if available
                metadata = get_file_metadata(source_path)
                
                # Convert file
                converted_content = converter.convert_to_spring_boot(content, file_type, metadata)
                
                if converted_content:
                    # Determine target path
                    target_path = os.path.join(target_dir, convert_path(rel_path))
                    
                    # Create target directory if needed
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # Write converted file
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(converted_content)
                    
                    stats["converted"] += 1
                    print(f"✅ Converted: {rel_path}")
                else:
                    stats["failed"] += 1
                    print(f"❌ Failed to convert: {rel_path}")
                    
            except Exception as e:
                stats["failed"] += 1
                print(f"❌ Error converting {file}: {str(e)}")
    
    # Update statistics output to include static resources
    print("\n📊 Conversion Statistics:")
    print(f"✅ Converted: {stats['converted']} files")
    print(f"📦 Static Resources: {stats['static_resources']['copied']} copied, {stats['static_resources']['failed']} failed")
    print(f"❌ Failed: {stats['failed']} files")
    print(f"⏭️  Skipped: {stats['skipped']} files")
    
    return stats

def determine_file_type(file_path: str) -> str:
    """Determine the type of file based on path and content"""
    if file_path.endswith('.java'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '@Path' in content or '@RestController' in content:
            return "Controller"
        elif '@Stateless' in content or '@Service' in content:
            return "Service"
        elif '@Entity' in content:
            return "Entity"
        elif '@Repository' in content:
            return "Repository"
    elif file_path.endswith(('.xhtml', '.jsf')):
        return "View"
    
    return None

def get_file_metadata(file_path: str) -> Dict:
    """Get additional metadata about the file from Neo4j"""
    # TODO: Implement Neo4j metadata retrieval
    return {}

if __name__ == "__main__":
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        exit(1)
        
    source_dir = os.getenv('SOURCE_DIR', "/Users/jaiganeshg/projects/logicshift/jboss-eap-quickstarts/kitchensink/src")
    target_dir = os.getenv('TARGET_DIR', "/Users/jaiganeshg/projects/logicshift/migrated-project")
    
    stats = convert_project(source_dir, target_dir, api_key)
    
    print("\n📊 Conversion Statistics:")
    print(f"✅ Converted: {stats['converted']} files")
    print(f"📦 Static Resources: {stats['static_resources']['copied']} copied, {stats['static_resources']['failed']} failed")
    print(f"❌ Failed: {stats['failed']} files")
    print(f"⏭️  Skipped: {stats['skipped']} files") 