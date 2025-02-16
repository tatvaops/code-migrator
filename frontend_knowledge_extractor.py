import os
from bs4 import BeautifulSoup
from neo4j import GraphDatabase

class FrontendExtractor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, params={}):
        """Execute Cypher query in Neo4j"""
        with self.driver.session() as session:
            session.run(query, params)

    def add_page(self, name, file_path, template_type):
        """Store page information in the graph"""
        query = """
        MERGE (p:Page {name: $name})
        SET p.filePath = $file_path,
            p.templateType = $template_type
        """
        self.execute_query(query, {
            "name": name,
            "file_path": file_path,
            "template_type": template_type
        })

    def add_form(self, page_name, form_id, action, method):
        """Store form information"""
        query = """
        MATCH (p:Page {name: $page_name})
        MERGE (f:Form {id: $form_id})
        SET f.action = $action,
            f.method = $method
        MERGE (p)-[:CONTAINS]->(f)
        """
        self.execute_query(query, {
            "page_name": page_name,
            "form_id": form_id or "unnamed_form",
            "action": action,
            "method": method
        })

    def add_form_field(self, page_name, form_id, field_name, field_type, validation=None):
        """Store form field information"""
        query = """
        MATCH (p:Page {name: $page_name})-[:CONTAINS]->(f:Form {id: $form_id})
        MERGE (field:FormField {name: $field_name})
        SET field.type = $field_type,
            field.validation = $validation
        MERGE (f)-[:HAS_FIELD]->(field)
        """
        self.execute_query(query, {
            "page_name": page_name,
            "form_id": form_id or "unnamed_form",
            "field_name": field_name,
            "field_type": field_type,
            "validation": validation
        })

    def add_template_relationship(self, page_name, template_name):
        """Store template relationships"""
        query = """
        MATCH (p:Page {name: $page_name})
        MERGE (t:Template {name: $template_name})
        MERGE (p)-[:USES_TEMPLATE]->(t)
        """
        self.execute_query(query, {
            "page_name": page_name,
            "template_name": template_name
        })

    def add_resource_dependency(self, page_name, resource_type, resource_path):
        """Store resource dependencies (CSS, JS, etc.)"""
        query = """
        MATCH (p:Page {name: $page_name})
        MERGE (r:Resource {path: $resource_path})
        SET r.type = $resource_type
        MERGE (p)-[:DEPENDS_ON]->(r)
        """
        self.execute_query(query, {
            "page_name": page_name,
            "resource_type": resource_type,
            "resource_path": resource_path
        })

def extract_frontend_info(directory, extractor):
    """Extract information from XHTML and HTML files"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.xhtml', '.html')):
                file_path = os.path.join(root, file)
                template_type = 'xhtml' if file.endswith('.xhtml') else 'html'
                page_name = os.path.splitext(file)[0]

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        soup = BeautifulSoup(content, 'html.parser')

                        # Add page to graph
                        extractor.add_page(page_name, file_path, template_type)

                        # Extract forms
                        forms = soup.find_all('form')
                        for form in forms:
                            form_id = form.get('id', 'unnamed_form')
                            action = form.get('action', '')
                            method = form.get('method', 'get')

                            extractor.add_form(page_name, form_id, action, method)

                            # Extract form fields
                            for field in form.find_all(['input', 'select', 'textarea']):
                                field_name = field.get('name', '')
                                field_type = field.get('type', field.name)
                                validation = {
                                    'required': field.get('required') is not None,
                                    'pattern': field.get('pattern'),
                                    'minlength': field.get('minlength'),
                                    'maxlength': field.get('maxlength')
                                }
                                
                                if field_name:
                                    extractor.add_form_field(
                                        page_name, 
                                        form_id, 
                                        field_name, 
                                        field_type, 
                                        validation
                                    )

                        # Extract template relationships
                        templates = soup.find_all(attrs={'template': True})
                        for template in templates:
                            template_name = template.get('template')
                            if template_name:
                                extractor.add_template_relationship(page_name, template_name)

                        # Extract resource dependencies
                        # CSS files
                        for css in soup.find_all('link', rel='stylesheet'):
                            href = css.get('href')
                            if href:
                                extractor.add_resource_dependency(page_name, 'css', href)

                        # JavaScript files
                        for js in soup.find_all('script', src=True):
                            src = js.get('src')
                            if src:
                                extractor.add_resource_dependency(page_name, 'javascript', src)

                        # Images
                        for img in soup.find_all('img', src=True):
                            src = img.get('src')
                            if src:
                                extractor.add_resource_dependency(page_name, 'image', src)

                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    directory_path = "/Users/jaiganeshg/projects/logicshift/jboss-eap-quickstarts/kitchensink"
    frontend_extractor = FrontendExtractor("bolt://localhost:7687", "neo4j", "password")

    print("Extracting frontend details and inserting into Neo4j...")
    extract_frontend_info(directory_path, frontend_extractor)

    print("Frontend knowledge graph setup complete!")
    frontend_extractor.close() 