from neo4j import GraphDatabase
import os
import javalang

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

class KnowledgeGraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    def close(self):
        self.driver.close()

    def execute_query(self, query, params={}):
        with self.driver.session() as session:
            session.run(query, params)

    def add_jakarta_controller(self, name, package, file_path):
        query = """
        MERGE (c:Controller {name: $name})
        SET c.package = $package, 
            c.filePath = $file_path,
            c.type = 'Controller'
        """
        self.execute_query(query, {"name": name, "package": package, "file_path": file_path})

    def add_service(self, name, package, file_path):
        query = """
        MERGE (s:Service {name: $name})
        SET s.package = $package, 
            s.filePath = $file_path,
            s.type = 'Service'
        """
        self.execute_query(query, {"name": name, "package": package, "file_path": file_path})

    def add_model(self, name, package, file_path):
        query = """
        MERGE (m:Model {name: $name})
        SET m.package = $package, 
            m.filePath = $file_path,
            m.type = 'Model'
        """
        self.execute_query(query, {"name": name, "package": package, "file_path": file_path})

    def add_repository(self, name, package, file_path):
        query = """
        MERGE (r:Repository {name: $name})
        SET r.package = $package, 
            r.filePath = $file_path,
            r.type = 'Repository'
        """
        self.execute_query(query, {"name": name, "package": package, "file_path": file_path})

    def add_dependency(self, caller, callee):
        query = """
        MERGE (a {name: $caller})
        MERGE (b {name: $callee})
        MERGE (a)-[:DEPENDS_ON]->(b)
        """
        self.execute_query(query, {"caller": caller, "callee": callee})

    def add_controller_action(self, controller_name, method_name, http_method, path):
        query = """
        MATCH (c:Controller {name: $controller_name})
        MERGE (a:Action {name: $method_name})
        SET a.httpMethod = $http_method,
            a.path = $path
        MERGE (c)-[:HAS_ACTION]->(a)
        """
        self.execute_query(query, {
            "controller_name": controller_name,
            "method_name": method_name,
            "http_method": http_method,
            "path": path
        })


# Function to parse Java files
def parse_java_files(directory, graph):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    source_code = f.read()

                try:
                    tree = javalang.parse.parse(source_code)
                except javalang.parser.JavaSyntaxError:
                    print(f"⚠️ Syntax error in {file_path}, skipping...")
                    continue

                package = None
                class_name = None
                annotations = set()
                field_types = set()

                # Extract package name
                for path, node in tree:
                    if isinstance(node, javalang.tree.PackageDeclaration):
                        package = node.name

                # Extract class names, annotations and field types
                for path, node in tree:
                    if isinstance(node, javalang.tree.ClassDeclaration):
                        class_name = node.name
                        for annotation in node.annotations:
                            annotations.add(annotation.name)
                    
                    # Collect field types for dependency analysis
                    if isinstance(node, javalang.tree.FieldDeclaration):
                        for declarator in node.declarators:
                            if hasattr(node.type, 'name'):
                                field_types.add(node.type.name)

                # Enhanced component detection
                controller_annotations = {'Controller', 'RestController', 'Path', 'RequestMapping'}
                service_annotations = {'Service', 'ApplicationScoped', 'RequestScoped', 'Stateless', 'Stateful'}
                model_annotations = {'Entity', 'Model', 'Document', 'MappedSuperclass'}
                repository_annotations = {'Repository', 'PersistenceContext'}

                # Make controller detection take precedence
                if annotations.intersection(controller_annotations):
                    graph.add_jakarta_controller(class_name, package, file_path)
                elif annotations.intersection(service_annotations):
                    graph.add_service(class_name, package, file_path)
                elif annotations.intersection(repository_annotations):
                    graph.add_repository(class_name, package, file_path)
                elif annotations.intersection(model_annotations):
                    graph.add_model(class_name, package, file_path)

                # Parse controller methods
                for path, node in tree:
                    if isinstance(node, javalang.tree.MethodDeclaration):
                        parse_controller_methods(node, class_name, node.annotations, graph)

                # Add dependencies based on field types and method parameters
                for field_type in field_types:
                    if class_name and field_type != class_name:  # Avoid self-references
                        graph.add_dependency(class_name, field_type)

                # Detect method dependencies
                for path, node in tree:
                    if isinstance(node, javalang.tree.MethodInvocation):
                        if node.qualifier and node.qualifier != class_name:
                            graph.add_dependency(class_name, node.qualifier)
                    
                    # Add parameter type dependencies
                    if isinstance(node, javalang.tree.MethodDeclaration):
                        for param in node.parameters:
                            if hasattr(param.type, 'name'):
                                param_type = param.type.name
                                if param_type != class_name:
                                    graph.add_dependency(class_name, param_type)

def parse_controller_methods(node, class_name, annotations, graph):
    if not isinstance(node, javalang.tree.MethodDeclaration):
        return

    method_name = node.name
    http_method = None
    path = None

    # Check method annotations for REST/Web endpoints
    for annotation in node.annotations:
        anno_name = annotation.name
        if anno_name in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            http_method = anno_name
        
        # Extract path from @Path annotation
        if anno_name == 'Path':
            if annotation.element and annotation.element.value:
                # Remove quotes from the path value
                path = annotation.element.value.strip('"\'')

    if http_method or path:
        graph.add_controller_action(class_name, method_name, http_method, path)


if __name__ == "__main__":
    directory_path = "/Users/jaiganeshg/projects/logicshift/jboss-eap-quickstarts/kitchensink"
    graph_builder = KnowledgeGraphBuilder()
    
    print("Extracting Jakarta EE components and inserting into Neo4j...")
    parse_java_files(directory_path, graph_builder)

    print("Knowledge graph setup complete! ✅")
    graph_builder.close()
