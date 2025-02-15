import os
from neo4j import GraphDatabase
from pathlib import Path
import shutil
from config import *
from generators.component_generator import ComponentGenerator
from utils.file_writer import FileWriter

class SpringBootMigrator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.file_writer = FileWriter()
        self.component_generator = ComponentGenerator(self.file_writer)
        
    def close(self):
        self.driver.close()

    def fetch_project_structure(self):
        """Fetch all components and their details from Neo4j"""
        query = """
        MATCH (n)
        WHERE n:Controller OR n:Service OR n:Repository OR n:Model OR n:Entity
        OPTIONAL MATCH (n)-[:HAS_COLUMN]->(c:Column)
        RETURN n.name AS name,
               labels(n)[0] as type,
               n.package as package,
               COLLECT({
                   name: c.name,
                   type: c.type,
                   constraints: c.constraints
               }) as columns
        """
        with self.driver.session() as session:
            return [dict(record) for record in session.run(query)]

    def create_spring_boot_project(self, target_dir):
        """Create Spring Boot project structure"""
        base_package = "com.example.migration"
        base_package_path = os.path.join(target_dir, "src/main/java", base_package.replace(".", "/"))
        
        # Create directory structure
        directories = [
            "controllers",
            "services",
            "repositories",
            "models",
            "config",
            "exceptions"
        ]
        
        for dir_name in directories:
            Path(os.path.join(base_package_path, dir_name)).mkdir(parents=True, exist_ok=True)
            
        # Create pom.xml
        self._create_pom_xml(target_dir)
        
        # Create application.properties
        self._create_application_properties(target_dir)
        
        # Create main application class
        self._create_main_class(base_package_path)
        
        return base_package_path

    def migrate_components(self, components, base_package_path):
        """Generate Spring Boot components from Jakarta EE components"""
        for component in components:
            component_type = component["type"]
            name = component["name"]
            columns = component["columns"]
            
            # Clean up component names
            if name.endswith("Controller") or name.endswith("Resource"):
                clean_name = name.replace("Resource", "").replace("Controller", "")
                self.component_generator.create_controller(
                    f"{clean_name}Controller", 
                    clean_name, 
                    columns, 
                    base_package_path
                )
                continue
                
            if name.endswith("Service"):
                clean_name = name.replace("Service", "")
                self.component_generator.create_service(
                    f"{clean_name}Service", 
                    clean_name, 
                    base_package_path
                )
                continue
                
            if name.endswith("Repository"):
                clean_name = name.replace("Repository", "")
                self.component_generator.create_repository(
                    f"{clean_name}Repository", 
                    clean_name, 
                    base_package_path
                )
                continue
                
            # Assume it's a model if no specific suffix
            if component_type in ["Model", "Entity"]:
                self.component_generator.create_model(name, columns, base_package_path)

    def _create_pom_xml(self, target_dir):
        self.component_generator.create_pom_xml(target_dir)

    def _create_application_properties(self, target_dir):
        self.component_generator.create_application_properties(target_dir)

    def _create_main_class(self, base_path):
        self.component_generator.create_main_class(base_path)

if __name__ == "__main__":
    # Neo4j Connection Details
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "password"

    # Target directory for the new Spring Boot project
    target_directory = "/Users/jaiganeshg/projects/logicshift/migrated-project"

    migrator = SpringBootMigrator(neo4j_uri, neo4j_user, neo4j_password)
    
    print("🚀 Starting Spring Boot migration...")
    
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
    
    migrator.close() 