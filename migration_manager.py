from converters.controller_converter import ControllerConverter
from converters.service_converter import ServiceConverter
from converters.repository_converter import RepositoryConverter
from converters.entity_converter import EntityConverter
from converters.view_converter import ViewConverter
from utils.resource_handler import *
from utils.neo4j_handler import get_file_metadata
from typing import Dict
import os

class MigrationManager:
    def __init__(self, api_key: str):
        self.converters = {
            "Controller": ControllerConverter(api_key),
            "Service": ServiceConverter(api_key),
            "Repository": RepositoryConverter(api_key),
            "Entity": EntityConverter(api_key),
            "View": ViewConverter(api_key)
        }
    
    def convert_project(self, source_dir: str, target_dir: str):
        """Convert entire project from Jakarta EE to Spring Boot"""
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
        
        # Walk through source directory
        for root, _, files in os.walk(source_dir):
            for file in files:
                source_path = os.path.join(root, file)
                rel_path = os.path.relpath(source_path, source_dir)
                
                # Skip if it's a static resource
                if any(file.lower().endswith(ext) for ext in ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']):
                    continue
                    
                # Determine file type and whether it needs conversion
                file_type = determine_file_type(source_path)
                if not file_type:
                    print(f"⏭️  Skipping: {rel_path} (Unsupported file type)")
                    stats["skipped"] += 1
                    continue
                    
                print(f"\n{'='*80}")
                print(f"🔍 Processing: {rel_path}")
                print(f"📁 File Type: {file_type}")
                
                try:
                    # Read source file
                    with open(source_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Get metadata from Neo4j
                    metadata = get_file_metadata(source_path)
                    
                    # Convert file using appropriate converter
                    converter = self.converters.get(file_type)
                    if not converter:
                        print(f"❌ No converter found for type: {file_type}")
                        stats["failed"] += 1
                        continue
                        
                    converted_content = converter.convert(content, metadata)
                    
                    if converted_content:
                        # Update resource references if it's a view file
                        if file_type == "View":
                            converted_content = update_resource_references(converted_content)
                        
                        # Determine target path
                        target_path = os.path.join(target_dir, convert_path(rel_path))
                        
                        # Create target directory if needed
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        
                        # Write converted file
                        with open(target_path, 'w', encoding='utf-8') as f:
                            f.write(converted_content)
                        
                        stats["converted"] += 1
                        print(f"✅ Successfully converted: {rel_path}")
                    else:
                        stats["failed"] += 1
                        print(f"❌ Failed to convert: {rel_path}")
                        
                except Exception as e:
                    stats["failed"] += 1
                    print(f"❌ Error converting {file}: {str(e)}")
                
                print(f"{'='*80}\n")
        
        # Print final statistics
        print("\n📊 Conversion Statistics:")
        print(f"✅ Converted: {stats['converted']} files")
        print(f"📦 Static Resources: {stats['static_resources']['copied']} copied, {stats['static_resources']['failed']} failed")
        print(f"❌ Failed: {stats['failed']} files")
        print(f"⏭️  Skipped: {stats['skipped']} files")
        
        return stats 