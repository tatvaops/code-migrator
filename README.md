# Code Migration Assistant

A comprehensive tool for analyzing codebases and planning migrations to modern frameworks. This tool extracts knowledge from source code, documentation, and database structures to provide intelligent migration recommendations.

## Features

- 📦 Java component analysis
- 💾 Database structure extraction
- 🎨 Frontend component analysis
- 📄 Documentation analysis (Word & Markdown files)
- 🤖 AI-powered querying system
- 📊 Knowledge graph generation
- 📋 Comprehensive migration planning

## Prerequisites

- Python 3.8 or higher
- Neo4j Database (running locally or remote)
- Java Development Kit (JDK) 8 or higher

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/code-migration-assistant.git
cd code-migration-assistant
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables (optional):

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
export SOURCE_DIR="/path/to/your/project"
```

## Usage

### 1. Knowledge Extraction

Run the knowledge extraction process to analyze your codebase:

```bash
python extract_knowledge.py
```

This will:
- Analyze Java components and their relationships
- Extract database schemas and configurations
- Process frontend components
- Extract information from documentation (Word & Markdown files)
- Generate a knowledge graph
- Create a vector store for documentation

### 2. Migration Planning

Generate a migration plan based on the extracted knowledge:

```bash
python planner.py
```

This will create a detailed migration report with:
- Component dependencies
- Required framework updates
- Potential migration challenges
- Step-by-step migration recommendations

### 3. Migration Execution

Execute the migration process:

```bash
python migrator.py
```

### 4. Query the Knowledge Base

Ask questions about your codebase:

```bash
python query.py
```

Example queries:
- "What are the main dependencies of the project?"
- "Show me all database relationships"
- "List all API endpoints"
- "Find documentation about authentication"

## Project Structure

```
.
├── extract_knowledge.py      # Main knowledge extraction script
├── document_knowledge_extractor.py  # Documentation analysis
├── java_knowledge_extractor.py      # Java code analysis
├── database_knowledge_extractor.py  # Database structure analysis
├── frontend_knowledge_extractor.py  # Frontend component analysis
├── planner.py               # Migration planning
├── migrator.py             # Migration execution
├── query.py                # Knowledge base querying
└── vector_db/             # Vector database storage
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SOURCE_DIR | Path to the source code | Current directory |
| NEO4J_URI | Neo4j database URI | bolt://localhost:7687 |
| NEO4J_USER | Neo4j username | neo4j |
| NEO4J_PASSWORD | Neo4j password | password |

## Output Files

- `migration_report.txt`: Detailed migration recommendations
- `vector_db/`: Vector database containing documentation knowledge
- Neo4j database: Contains the code knowledge graph

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
