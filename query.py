from neo4j import GraphDatabase
import google.generativeai as genai
import os

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

# Google Gemini API Key
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

class KnowledgeGraphQuery:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    def close(self):
        self.driver.close()

    def execute_query(self, query, params={}):
        with self.driver.session() as session:
            result = session.run(query, params)
            return [record for record in result]

    def query_graph(self, user_question):
        prompt = f"""
        Convert this natural language query into a Cypher query for Neo4j:
        '{user_question}'
        
        The graph has these nodes and properties:
        - (Controller) with properties: name, package, filePath, type
        - (Service) with properties: name, package, filePath, type
        - (Model) with properties: name, package, filePath, type
        - (Repository) with properties: name, package, filePath, type
        - (Action) with properties: name, httpMethod, path
        - (UI) with properties: name, type (can be 'page', 'component', or 'template')
        - (Database) with properties: name, schema, tableName

        Relations:
        - (Controller)-[:DEPENDS_ON]->(Service)
        - (Service)-[:DEPENDS_ON]->(Repository)
        - (Controller)-[:HAS_ACTION]->(Action)
        - (UI)-[:CALLS]->(Controller)
        - (Model)-[:HAS_TABLE]->(Database)
        - (Repository)-[:USES]->(Database)
        
        Example queries:
        - Find UI components: MATCH (u:UI) RETURN u.name, u.type
        - Find database schema: MATCH (d:Database) RETURN d.name, d.schema
        - Find service details: MATCH (s:Service) WHERE s.name CONTAINS 'MemberResource' RETURN s
        - Find UI to database flow: MATCH p=(ui:UI)-[:CALLS]->(c:Controller)-[:DEPENDS_ON]->(s:Service)-[:DEPENDS_ON]->(r:Repository)-[:USES]->(db:Database) RETURN p
        - Find all actions of a service: MATCH (c:Controller)-[:HAS_ACTION]->(a:Action) WHERE c.name CONTAINS 'Member' RETURN a.name, a.httpMethod, a.path
        - Find database tables: MATCH (m:Model)-[:HAS_TABLE]->(d:Database) RETURN m.name, d.tableName

        Return only the Cypher query, no explanations.
        """

        # Generate Cypher query
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        cypher_query = response.text.strip('`').strip()

        print(f"Generated Cypher Query: \n{cypher_query}\n")

        # Execute Cypher query
        data = self.execute_query(cypher_query)
        formatted_data = [dict(record) for record in data]

        # Generate final answer using LLM
        answer_prompt = f"""
        Based on this query result from a Jakarta EE application's structure: {formatted_data}
        
        Answer the question: '{user_question}'
        
        For UI questions: List all UI components and their types
        For database schema: Show the schema structure and related tables
        For service questions: Show the service name, its controllers, and repositories
        
        Format the response in a clear, structured way using bullet points.
        Include all technical details available.
        If no data was found, explain what was searched for and that no results were found.
        """
        final_response = model.generate_content(answer_prompt)

        return final_response.text

    def add_common_queries(self):
        """Add some predefined queries for common questions"""
        self.common_queries = {
            "ui": "MATCH (u:UI) RETURN u.name, u.type",
            "database schema": """
                MATCH (d:Database)
                OPTIONAL MATCH (m:Model)-[:HAS_TABLE]->(d)
                RETURN d.schema, collect(m.name) as tables
            """,
            "service details": """
                MATCH (s:Service)
                OPTIONAL MATCH (c:Controller)-[:DEPENDS_ON]->(s)
                OPTIONAL MATCH (s)-[:DEPENDS_ON]->(r:Repository)
                RETURN s.name as name, 
                       collect(DISTINCT c.name) as controllers, 
                       collect(DISTINCT r.name) as repositories,
                       s.package as package
            """
        }

    def get_service_details(self, service_name):
        query = """
        MATCH (s:Service)
        WHERE s.name CONTAINS $service_name
        OPTIONAL MATCH (c:Controller)-[:DEPENDS_ON]->(s)
        OPTIONAL MATCH (s)-[:DEPENDS_ON]->(r:Repository)
        OPTIONAL MATCH (c)-[:HAS_ACTION]->(a:Action)
        RETURN s.name as name,
               s.package as package,
               collect(DISTINCT c.name) as controllers,
               collect(DISTINCT r.name) as repositories,
               collect(DISTINCT {method: a.httpMethod, path: a.path, name: a.name}) as actions
        """
        return self.execute_query(query, {"service_name": service_name})

if __name__ == "__main__":
    graph_query = KnowledgeGraphQuery()
    graph_query.add_common_queries()

    print("\nWelcome to the Jakarta EE System Query Tool!")
    print("You can ask questions about:")
    print("- UI components and pages")
    print("- Database schema and tables")
    print("- Controllers and their actions")
    print("- Services and their responsibilities")
    print("- Component dependencies")
    print("- System architecture")

    while True:
        user_input = input("\nAsk a question about the Jakarta EE system (or type 'exit'): ")
        if user_input.lower() == "exit":
            break

        try:
            if "MemberResourceRESTService" in user_input:
                data = graph_query.get_service_details("MemberResource")
                formatted_data = [dict(record) for record in data]
                
                answer_prompt = f"""
                Based on this service information: {formatted_data}
                
                Provide a detailed description of the MemberResourceRESTService, including:
                - Its package location
                - What controllers use it
                - What repositories it depends on
                - What REST actions it provides
                
                Format as bullet points and include all technical details.
                """
                model = genai.GenerativeModel("gemini-pro")
                answer = model.generate_content(answer_prompt).text
            else:
                answer = graph_query.query_graph(user_input)
            
            print("\n💡 Answer:\n", answer)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

    graph_query.close()
