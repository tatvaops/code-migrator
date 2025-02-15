#!/usr/bin/env python3

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from migrator import SpringBootMigrator

def main():
    # Neo4j Connection Details
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "password"

    # Target directory for the new Spring Boot project
    target_directory = "/Users/jaiganeshg/projects/logicshift/migrated-project"

    migrator = SpringBootMigrator(neo4j_uri, neo4j_user, neo4j_password)
    
    print("🚀 Starting Spring Boot migration...")
    
    try:
        # Create new project structure
        print("📁 Creating project structure...")
        base_package_path = migrator.create_spring_boot_project(target_directory)
        
        # Fetch and migrate components
        print("🔄 Migrating components...")
        components = migrator.fetch_project_structure()
        migrator.migrate_components(components, base_package_path)
        
        print("✅ Migration complete! New Spring Boot project created at:", target_directory)
        print("\nNext steps:")
        print("1. Review the generated code")
        print("2. Update MongoDB connection settings in application.properties")
        print("3. Run 'mvn clean install' to build the project")
        print("4. Start MongoDB")
        print("5. Run the application using 'mvn spring-boot:run'")
    
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
    finally:
        migrator.close()

if __name__ == "__main__":
    main() 