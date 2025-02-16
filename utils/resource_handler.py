import os
import shutil
import re
from typing import Dict

def determine_file_type(file_path: str) -> str:
    """Determine the type of file based on path and content"""
    if file_path.endswith('.java'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '@Path' in content or '@RestController' in content:
            return "Controller"
        elif '@Stateless' in content or '@Service' in content:
            return "Service"
        elif '@Entity' in content or '@Document' in content:
            return "Entity"
        elif '@Repository' in content or 'extends JpaRepository' in content:
            return "Repository"
    elif file_path.endswith(('.xhtml', '.jsf', '.jsp')):
        return "View"
    
    return None

def convert_path(path: str) -> str:
    if path.lower().endswith(('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot')):
        return os.path.join('src/main/resources/static', path.replace('webapp/', ''))
    if path.endswith(('.xhtml', '.jsf')):
        path = os.path.splitext(path)[0] + '.html'
        return os.path.join('src/main/resources/templates', path.replace('webapp/', ''))
    return path

def copy_static_resources(source_dir: str, target_dir: str) -> Dict[str, int]:
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
    
    # Update relative paths
    content = re.sub(
        r'(href|src)="(?!@{)(.*?\.(css|js|jpg|jpeg|png|gif|svg))"',
        r'\1="@{/\2}"',
        content
    )
    
    return content 