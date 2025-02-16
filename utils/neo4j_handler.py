from neo4j import GraphDatabase
import os
from typing import Dict, Optional

def get_file_metadata(file_path: str) -> Optional[Dict]:
    """Get additional metadata about the file from Neo4j"""
    try:
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        if not password:
            print(f"⚠️  NEO4J_PASSWORD not set, skipping metadata for {file_path}")
            return None
            
        with GraphDatabase.driver(uri, auth=(user, password)) as driver:
            with driver.session() as session:
                # Query file metadata and relationships
                result = session.run("""
                    MATCH (f:File {path: $file_path})
                    OPTIONAL MATCH (f)-[r]->(related)
                    RETURN f.type as type,
                           collect(DISTINCT {
                               type: type(r),
                               target: related.path,
                               targetType: related.type
                           }) as relationships,
                           f.imports as imports,
                           f.dependencies as dependencies
                    """, file_path=file_path)
                
                data = result.single()
                if not data:
                    print(f"⚠️  No metadata found for {file_path}")
                    return None
                    
                metadata = {
                    "type": data["type"],
                    "relationships": data["relationships"],
                    "imports": data["imports"],
                    "dependencies": data["dependencies"]
                }
                
                print(f"📊 Retrieved metadata for {os.path.basename(file_path)}:")
                print(f"  - Type: {metadata['type']}")
                print(f"  - Dependencies: {len(metadata.get('dependencies', []))} found")
                print(f"  - Relationships: {len(metadata.get('relationships', []))} found")
                
                return metadata
                
    except Exception as e:
        print(f"⚠️  Error retrieving Neo4j metadata: {str(e)}")
        return None 