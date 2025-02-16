import os
from migration_manager import MigrationManager

def main():
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        exit(1)
    
    # Get source and target directories from environment or use defaults
    source_dir = os.getenv('SOURCE_DIR', "/Users/jaiganeshg/projects/logicshift/jboss-eap-quickstarts/kitchensink/src")
    target_dir = os.getenv('TARGET_DIR', "/Users/jaiganeshg/projects/logicshift/migrated-project")
    
    if not source_dir or not target_dir:
        print("❌ Please set SOURCE_DIR and TARGET_DIR environment variables")
        print("Example:")
        print("export SOURCE_DIR=/path/to/jakarta/project")
        print("export TARGET_DIR=/path/to/output/spring/project")
        exit(1)
    
    # Initialize migration manager
    manager = MigrationManager(api_key)
    
    # Run the conversion
    try:
        stats = manager.convert_project(source_dir, target_dir)
        
        # Print summary
        print("\n✨ Migration Complete!")
        print(f"Source: {source_dir}")
        print(f"Target: {target_dir}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 