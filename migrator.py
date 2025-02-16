import os
from migration_manager import MigrationManager

def main():
    # Get required environment variables
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        exit(1)
    
    # Get source and target directories
    source_dir = os.getenv('SOURCE_DIR', "/Users/jaiganeshg/projects/logicshift/jboss-eap-quickstarts/kitchensink/src")
    target_dir = os.getenv('TARGET_DIR', "/Users/jaiganeshg/projects/logicshift/migrated-project")
    
    if not source_dir or not target_dir:
        print("❌ Please set SOURCE_DIR and TARGET_DIR environment variables")
        print("Example:")
        print("export SOURCE_DIR=/path/to/jakarta/project")
        print("export TARGET_DIR=/path/to/output/spring/project")
        exit(1)
    
    # Get package namespace
    namespace = os.getenv('PACKAGE_NAMESPACE', "com.mongodb.kitchensink.demo")
    if not namespace:
        print("⚠️  PACKAGE_NAMESPACE not set, will use default 'com.example.application'")
    
    # Initialize migration manager
    manager = MigrationManager(api_key)
    
    # Run the conversion
    try:
        stats = manager.convert_project(source_dir, target_dir)
        print("\n✨ Migration Complete!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 