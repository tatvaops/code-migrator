#!/usr/bin/env python3

import os
from java_knowledge_extractor import KnowledgeGraphBuilder, parse_java_files as parse_java_components
from database_knowledge_extractor import DatabaseExtractor, parse_java_files as parse_database_files, detect_database_config
from frontend_knowledge_extractor import FrontendExtractor, extract_frontend_info
from planner import MigrationPlanner
from document_knowledge_extractor import DocumentExtractor

class KnowledgeExtraction:
    def __init__(self, source_dir, neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="password"):
        self.source_dir = source_dir
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # Initialize all extractors
        self.java_extractor = KnowledgeGraphBuilder()
        self.db_extractor = DatabaseExtractor(neo4j_uri, neo4j_user, neo4j_password)
        self.frontend_extractor = FrontendExtractor(neo4j_uri, neo4j_user, neo4j_password)
        self.planner = MigrationPlanner(neo4j_uri, neo4j_user, neo4j_password)
        self.doc_extractor = DocumentExtractor()

    def extract_all(self):
        """Run all extractors and generate migration report"""
        try:
            print("\n🔍 Starting knowledge extraction process...")

            # 1. Extract Java components
            print("\n📦 Analyzing Java components...")
            parse_java_components(self.source_dir, self.java_extractor)
            print("✅ Java component analysis complete")

            # 2. Extract database information
            print("\n💾 Analyzing database structure...")
            detect_database_config(self.source_dir, self.db_extractor)
            parse_database_files(self.source_dir, self.db_extractor)
            print("✅ Database analysis complete")

            # 3. Extract frontend information
            print("\n🎨 Analyzing frontend components...")
            extract_frontend_info(self.source_dir, self.frontend_extractor)
            print("✅ Frontend analysis complete")

            # Add document extraction step
            print("\n📄 Analyzing documentation...")
            doc_contents = self.doc_extractor.process_documents(self.source_dir)
            if doc_contents:
                self.doc_extractor.create_vector_store(doc_contents)
                print(f"✅ Processed {len(doc_contents)} documentation files")
            else:
                print("ℹ️ No documentation files (.docx or .md) found")

            # 4. Generate comprehensive migration report
            print("\n📋 Generating migration report...")
            self.planner.save_report("migration_report.txt")
            print("✅ Migration report generated")

            print("\n✨ Knowledge extraction complete!")
            print("\nNext steps:")
            print("1. Review the migration report in 'migration_report.txt'")
            print("2. Use the Spring Boot migrator to generate the new project")
            print("3. Follow the migration recommendations in the report")

        except Exception as e:
            print(f"\n❌ Error during extraction: {str(e)}")
            raise  # Re-raise to see full traceback
        finally:
            self.cleanup()

    def cleanup(self):
        """Close all connections"""
        try:
            self.java_extractor.close()
            self.db_extractor.close()
            self.frontend_extractor.close()
            self.planner.close()
            self.doc_extractor.close()
        except Exception as e:
            print(f"Warning: Error during cleanup: {str(e)}")

def main():
    # Get source directory from environment variable or use default
    source_dir = os.getenv('SOURCE_DIR', "/Users/jaiganeshg/projects/logicshift/jboss-eap-quickstarts/kitchensink")
    
    # Neo4j connection details from environment variables or defaults
    neo4j_uri = os.getenv('NEO4J_URI', "bolt://localhost:7687")
    neo4j_user = os.getenv('NEO4J_USER', "neo4j")
    neo4j_password = os.getenv('NEO4J_PASSWORD', "password")

    extractor = KnowledgeExtraction(
        source_dir=source_dir,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password
    )
    
    extractor.extract_all()

if __name__ == "__main__":
    main() 