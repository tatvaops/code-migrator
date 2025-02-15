import os
import javalang
from neo4j import GraphDatabase

class DatabaseExtractor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, params={}):
        """Execute Cypher query in Neo4j"""
        with self.driver.session() as session:
            session.run(query, params)

    def add_database_info(self, db_type, config_file):
        """Store database type in the graph"""
        query = """
        MERGE (db:Database {type: $db_type, configFile: $config_file})
        """
        self.execute_query(query, {"db_type": db_type, "config_file": config_file})

    def add_table(self, table_name, entity_name, columns=None):
        """Store database tables (from JPA entities)"""
        query = """
        MERGE (t:Table {name: $table_name})
        MERGE (e:Entity {name: $entity_name})
        SET t.columns = $columns
        MERGE (e)-[:MAPS_TO]->(t)
        """
        self.execute_query(query, {
            "table_name": table_name, 
            "entity_name": entity_name,
            "columns": columns or []
        })

    def add_column(self, table_name, column_name, column_type, constraints=None):
        """Store column information"""
        query = """
        MATCH (t:Table {name: $table_name})
        MERGE (c:Column {name: $column_name, type: $column_type})
        SET c.constraints = $constraints
        MERGE (t)-[:HAS_COLUMN]->(c)
        """
        self.execute_query(query, {
            "table_name": table_name,
            "column_name": column_name,
            "column_type": column_type,
            "constraints": constraints or []
        })

    def add_model_details(self, entity_name, table_name, variables, methods):
        """Store detailed model information including methods and variables"""
        query = """
        MERGE (e:Entity {name: $entity_name})
        MERGE (t:Table {name: $table_name})
        SET e.variables = $variables,
            e.methods = $methods
        MERGE (e)-[:MAPS_TO]->(t)
        """
        self.execute_query(query, {
            "entity_name": entity_name,
            "table_name": table_name,
            "variables": variables,
            "methods": methods
        })

def extract_table_name(class_node):
    """Extract table name from @Table annotation"""
    table_name = None
    for annotation in class_node.annotations:
        if annotation.name == "Table":
            # Try to get table name from annotation
            if hasattr(annotation, 'element'):
                if hasattr(annotation.element, 'elements'):
                    # Handle case where annotation has multiple elements
                    for element in annotation.element.elements:
                        if hasattr(element, 'name') and element.name == "name":
                            table_name = element.value.strip('"')
                elif hasattr(annotation.element, 'value'):
                    # Handle case where annotation has single value
                    table_name = annotation.element.value.strip('"')
    
    return table_name

def parse_java_files(directory, db_extractor):
    """Extract DB details from Java files"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
                
                try:
                    tree = javalang.parse.parse(source_code)
                    
                    for _, node in tree:
                        if isinstance(node, javalang.tree.ClassDeclaration):
                            is_entity = False
                            entity_name = None
                            table_name = None
                            methods = []
                            variables = []

                            # Check for @Entity annotation
                            for annotation in node.annotations:
                                if annotation.name == "Entity":
                                    is_entity = True
                                    entity_name = node.name
                                    table_name = extract_table_name(node) or entity_name.lower()

                            if is_entity:
                                # Process fields/variables
                                for field in node.fields:
                                    field_name = field.declarators[0].name
                                    field_type = field.type.name
                                    constraints = []
                                    annotations = []

                                    # Extract field metadata from annotations
                                    for annotation in field.annotations:
                                        annotations.append(annotation.name)
                                        if annotation.name == "Column":
                                            for element in getattr(annotation.element, 'elements', []):
                                                if element.name == "name":
                                                    field_name = element.value.strip('"')
                                        constraints.append(annotation.name)

                                    variables.append({
                                        "name": field_name,
                                        "type": field_type,
                                        "constraints": constraints,
                                        "annotations": annotations
                                    })

                                # Process methods
                                for method in node.methods:
                                    method_info = {
                                        "name": method.name,
                                        "return_type": method.return_type.name if method.return_type else "void",
                                        "parameters": [],
                                        "annotations": [ann.name for ann in method.annotations]
                                    }
                                    
                                    # Get method parameters
                                    for param in method.parameters:
                                        param_info = {
                                            "name": param.name,
                                            "type": param.type.name
                                        }
                                        method_info["parameters"].append(param_info)
                                    
                                    methods.append(method_info)

                                # Add model details to graph
                                db_extractor.add_model_details(
                                    entity_name,
                                    table_name,
                                    variables,
                                    methods
                                )

                except Exception as e:
                    print(f"Failed to parse {file_path}: {str(e)}")
                    continue

def detect_database_config(directory, db_extractor):
    """Extract DB type from config files"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "persistence.xml":
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if "hibernate.dialect" in content:
                        if "MySQL" in content:
                            db_extractor.add_database_info("MySQL", file_path)
                        elif "PostgreSQL" in content:
                            db_extractor.add_database_info("PostgreSQL", file_path)
                        elif "Oracle" in content:
                            db_extractor.add_database_info("Oracle", file_path)
                        elif "H2" in content:
                            db_extractor.add_database_info("H2", file_path)
                        else:
                            db_extractor.add_database_info("Unknown", file_path)
                except Exception as e:
                    print(f"Failed to process {file_path}: {str(e)}")

if __name__ == "__main__":
    directory_path = "/Users/jaiganeshg/projects/logicshift/jboss-eap-quickstarts/kitchensink"
    db_extractor = DatabaseExtractor("bolt://localhost:7687", "neo4j", "password")

    print("Extracting database details and inserting into Neo4j...")
    detect_database_config(directory_path, db_extractor)
    parse_java_files(directory_path, db_extractor)

    print("Database knowledge graph setup complete!")
    db_extractor.close()
