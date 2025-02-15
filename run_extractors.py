from kl import KnowledgeGraphBuilder
from dkl import DatabaseExtractor
from frontend_extractor import FrontendExtractor

def run_all_extractors(directory_path):
    # Neo4j connection details
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "password"

    # Initialize extractors
    java_extractor = KnowledgeGraphBuilder()
    db_extractor = DatabaseExtractor(neo4j_uri, neo4j_user, neo4j_password)
    frontend_extractor = FrontendExtractor(neo4j_uri, neo4j_user, neo4j_password)

    try:
        print("1. Extracting Java components...")
        parse_java_files(directory_path, java_extractor)

        print("2. Extracting database information...")
        detect_database_config(directory_path, db_extractor)
        parse_java_files(directory_path, db_extractor)

        print("3. Extracting frontend information...")
        extract_frontend_info(directory_path, frontend_extractor)

        print("✅ Knowledge graph setup complete!")

    finally:
        # Close all connections
        java_extractor.close()
        db_extractor.close()
        frontend_extractor.close()

if __name__ == "__main__":
    directory_path = "/Users/jaiganeshg/projects/logicshift/jboss-eap-quickstarts/kitchensink"
    run_all_extractors(directory_path) 