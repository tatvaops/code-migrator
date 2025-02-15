from neo4j import GraphDatabase

class MigrationPlanner:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def analyze_project(self):
        """Analyze the project and generate migration recommendations"""
        report = []
        
        # Backend Analysis
        report.extend(self._analyze_backend_components())
        
        # Database Analysis
        report.extend(self._analyze_database())
        
        # Frontend Analysis
        report.extend(self._analyze_frontend())
        
        # Add detailed migration steps
        report.extend(self._generate_migration_steps())
        
        # Migration Recommendations
        report.extend(self._generate_recommendations())
        
        return report

    def _analyze_backend_components(self):
        """Analyze backend components and their relationships"""
        report = [
            "\n=== Backend Components Analysis ===\n",
            "📊 Component Overview:"
        ]
        
        # Query to get all components and their relationships
        query = """
        MATCH (n)
        WHERE n:Controller OR n:Service OR n:Repository OR n:Model OR n:Entity
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n.name as name, 
               labels(n)[0] as type,
               n.package as package,
               collect(distinct type(r)) as relationships,
               collect(distinct m.name) as dependencies
        """
        
        with self.driver.session() as session:
            results = session.run(query)
            
            # Group components by type
            components = {}
            for record in results:
                comp_type = record["type"]
                if comp_type not in components:
                    components[comp_type] = []
                components[comp_type].append({
                    "name": record["name"],
                    "package": record["package"],
                    "relationships": record["relationships"],
                    "dependencies": record["dependencies"]
                })
            
            # Generate report for each component type
            for comp_type, comps in components.items():
                report.append(f"\n🔹 {comp_type}s ({len(comps)} found):")
                for comp in comps:
                    report.append(f"\n  - {comp['name']}")
                    if comp['package']:
                        report.append(f"    Package: {comp['package']}")
                    if comp['dependencies']:
                        report.append(f"    Dependencies: {', '.join(filter(None, comp['dependencies']))}")
                    if comp['relationships']:
                        report.append(f"    Relationships: {', '.join(filter(None, comp['relationships']))}")

        return report

    def _analyze_database(self):
        """Analyze database structure and configurations"""
        report = ["\n=== Database Analysis ===\n"]
        
        with self.driver.session() as session:
            # Get database type and configuration
            db_info = session.run("""
                MATCH (db:Database)
                RETURN db.type as type, db.configFile as config
                LIMIT 1
            """)
            db_record = db_info.single()
            if db_record:
                report.extend([
                    "🔹 Database Configuration:",
                    f"  Type: {db_record['type']}",
                    f"  Config File: {db_record['config']}\n"
                ])

            # Get table structures
            tables = session.run("""
                MATCH (t:Table)
                OPTIONAL MATCH (t)-[:HAS_COLUMN]->(c:Column)
                RETURN t.name as table,
                       collect({
                           name: c.name,
                           type: c.type,
                           constraints: c.constraints
                       }) as columns
            """)
            
            report.append("🔹 Table Structures:")
            for record in tables:
                report.append(f"\n  Table: {record['table']}")
                for column in record["columns"]:
                    constraints = column["constraints"] or []
                    constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
                    report.append(f"    • {column['name']} ({column['type']}){constraint_str}")

            # Get entity details including methods and variables
            entities = session.run("""
                MATCH (e:Entity)
                RETURN e.name as name,
                       e.variables as variables,
                       e.methods as methods
            """)
            
            report.append("\n🔹 Entity Details:")
            for record in entities:
                report.append(f"\n  Entity: {record['name']}")
                
                # Report variables/fields
                if record['variables']:
                    report.append("    Variables:")
                    for var in record['variables']:
                        annotations = var.get('annotations', [])
                        annotation_str = f" [{', '.join(annotations)}]" if annotations else ""
                        report.append(f"      • {var['name']} ({var['type']}){annotation_str}")
                
                # Report methods
                if record['methods']:
                    report.append("    Methods:")
                    for method in record['methods']:
                        params = [f"{p['type']} {p['name']}" for p in method['parameters']]
                        param_str = ", ".join(params)
                        annotations = method.get('annotations', [])
                        annotation_str = f" [{', '.join(annotations)}]" if annotations else ""
                        report.append(f"      • {method['name']}({param_str}) -> {method['return_type']}{annotation_str}")

        return report

    def _analyze_frontend(self):
        """Analyze frontend components and templates"""
        report = ["\n=== Frontend Analysis ===\n"]

        with self.driver.session() as session:
            # Analyze pages and templates
            report.append("🔹 Pages and Templates:")
            pages = session.run("""
                MATCH (p:Page)
                OPTIONAL MATCH (p)-[:USES_TEMPLATE]->(t:Template)
                RETURN p.name as page,
                       p.filePath as path,
                       p.templateType as type,
                       collect(distinct t.name) as templates
            """)
            
            for record in pages:
                page_type = record["type"] or "html"
                templates = record["templates"]
                template_str = f" (uses templates: {', '.join(templates)})" if templates and templates[0] else ""
                report.extend([
                    f"\n  - {record['page']}.{page_type}",
                    f"    Path: {record['path']}{template_str}"
                ])

            # Analyze forms
            report.append("\n🔹 Forms and Validations:")
            forms = session.run("""
                MATCH (p:Page)-[:CONTAINS]->(f:Form)
                OPTIONAL MATCH (f)-[:HAS_FIELD]->(field:FormField)
                RETURN p.name as page,
                       f.id as form_id,
                       f.action as action,
                       f.method as method,
                       collect({
                           name: field.name,
                           type: field.type,
                           validation: field.validation
                       }) as fields
            """)
            
            for record in forms:
                report.extend([
                    f"\n  Form: {record['form_id']} in {record['page']}",
                    f"    Action: {record['action']}",
                    f"    Method: {record['method']}",
                    "    Fields:"
                ])
                
                for field in record["fields"]:
                    validation = field["validation"]
                    validation_str = ""
                    if validation:
                        validations = []
                        if validation.get("required"):
                            validations.append("required")
                        if validation.get("pattern"):
                            validations.append(f"pattern={validation['pattern']}")
                        if validation.get("minlength"):
                            validations.append(f"minlength={validation['minlength']}")
                        if validation.get("maxlength"):
                            validations.append(f"maxlength={validation['maxlength']}")
                        if validations:
                            validation_str = f" [{', '.join(validations)}]"
                    report.append(f"      • {field['name']} ({field['type']}){validation_str}")

            # Analyze resource dependencies
            report.append("\n🔹 Resource Dependencies:")
            resources = session.run("""
                MATCH (p:Page)-[:DEPENDS_ON]->(r:Resource)
                WITH r.type as type, count(r) as count, 
                     collect(distinct {path: r.path, page: p.name}) as resources
                RETURN type, count, resources
            """)
            
            for record in resources:
                report.append(f"\n  {record['type'].title()} Files ({record['count']}):")
                for resource in record["resources"]:
                    report.append(f"    • {resource['path']}")
                    report.append(f"      Used in: {resource['page']}")

        return report

    def _generate_migration_steps(self):
        """Generate specific migration steps for each component"""
        report = ["\n=== Detailed Migration Steps ===\n"]
        
        with self.driver.session() as session:
            # Get all components that need migration
            components = session.run("""
                MATCH (n)
                WHERE n:Controller OR n:Service OR n:Repository OR n:Model OR n:Entity
                OPTIONAL MATCH (n)-[:HAS_COLUMN]->(c:Column)
                RETURN n.name as name,
                       labels(n)[0] as type,
                       n.package as package,
                       collect({
                           name: c.name,
                           type: c.type,
                           constraints: COALESCE(c.constraints, [])
                       }) as columns
            """)
            
            for record in components:
                name = record["name"]
                comp_type = record["type"]
                package = record["package"]
                columns = record["columns"]
                
                report.append(f"\n🔹 {name} ({comp_type}):")
                report.append(f"  Source Package: {package}")
                
                if comp_type == "Controller":
                    report.extend([
                        "  Migration Steps:",
                        "    1. Replace @Path with @RequestMapping",
                        "    2. Convert class to @RestController",
                        "    3. Update method annotations:",
                        "       - @GET → @GetMapping",
                        "       - @POST → @PostMapping",
                        "       - @PUT → @PutMapping",
                        "       - @DELETE → @DeleteMapping",
                        "    4. Replace @PathParam with @PathVariable",
                        "    5. Replace @QueryParam with @RequestParam",
                        "    6. Replace @FormParam with @RequestParam",
                        "    7. Update response handling to use ResponseEntity",
                        "    8. Replace @Produces/@Consumes with produces/consumes attributes"
                    ])

                elif comp_type == "Service":
                    report.extend([
                        "  Migration Steps:",
                        "    1. Replace @Stateless/@Stateful with @Service",
                        "    2. Replace @EJB with @Autowired",
                        "    3. Replace @TransactionAttribute with @Transactional",
                        "    4. Update exception handling to use Spring exceptions",
                        "    5. Replace JNDI lookups with dependency injection",
                        "    6. Update transaction management to use Spring's approach"
                    ])

                elif comp_type == "Repository":
                    report.extend([
                        "  Migration Steps:",
                        "    1. Convert to Spring Data interface",
                        "    2. Extend MongoRepository<EntityType, String>",
                        "    3. Remove explicit EntityManager usage",
                        "    4. Convert JPQL queries to:",
                        "       - Method names (findByXxx)",
                        "       - @Query annotations",
                        "    5. Replace @PersistenceContext with Spring Data methods"
                    ])

                elif comp_type in ["Model", "Entity"]:
                    report.extend([
                        "  Migration Steps:",
                        "    1. Replace JPA annotations with MongoDB annotations:",
                        "       - @Entity → @Document",
                        "       - @Table → collection attribute in @Document",
                        "       - @Id remains (but from different package)",
                        "       - @Column → @Field",
                        "    2. Update field annotations:"
                    ])
                    
                    # Add specific field migrations if columns exist
                    if columns:
                        report.append("    Current fields to migrate:")
                        for column in columns:
                            constraints = column.get("constraints", [])
                            if not constraints:  # Handle empty constraints
                                constraints = []
                            report.append(f"      • {column['name']} ({column['type']}):")
                            
                            # Suggest specific annotation migrations
                            annotations = []
                            if "Id" in constraints:
                                annotations.append("@Id (from spring-data-mongodb)")
                            if "Column" in constraints:
                                annotations.append("@Field")
                            if "NotNull" in constraints:
                                annotations.append("@NotNull")
                            if "Size" in constraints:
                                annotations.append("@Size")
                            if "Email" in constraints:
                                annotations.append("@Email")
                            if annotations:
                                report.append(f"        Annotations: {', '.join(annotations)}")
                            else:
                                report.append("        No special annotations needed")

                report.extend([
                    "  Additional Considerations:",
                    "    - Update import statements to Spring Boot packages",
                    "    - Review and update exception handling",
                    "    - Add appropriate Spring Boot validation annotations",
                    "    - Update any Jakarta EE-specific code"
                ])

        return report

    def _generate_recommendations(self):
        """Generate migration recommendations based on analysis"""
        report = ["\n=== Migration Recommendations ===\n"]
        
        with self.driver.session() as session:
            # Backend recommendations
            backend_count = session.run("""
                MATCH (n)
                WHERE n:Controller OR n:Service OR n:Repository OR n:Model
                RETURN labels(n)[0] as type, count(n) as count
            """)
            
            report.append("🔹 Backend Migration:")
            for record in backend_count:
                report.append(f"  • Migrate {record['count']} {record['type']}(s) to Spring Boot equivalents")

            # Database recommendations
            db_info = session.run("MATCH (db:Database) RETURN db.type as type LIMIT 1").single()
            if db_info:
                report.extend([
                    "\n🔹 Database Migration:",
                    f"  • Current database: {db_info['type']}",
                    "  • Recommended actions:",
                    "    - Update database configuration in application.properties",
                    "    - Migrate JPA entities to Spring Data annotations",
                    "    - Update repository interfaces to extend Spring Data repositories"
                ])

            # Frontend recommendations
            frontend_info = session.run("""
                MATCH (p:Page)
                RETURN p.templateType as type, count(p) as count
            """)
            
            report.append("\n🔹 Frontend Migration:")
            for record in frontend_info:
                if record["type"] == "xhtml":
                    report.extend([
                        f"  • Convert {record['count']} XHTML templates to Thymeleaf",
                        "  • Replace JSF components with Thymeleaf equivalents",
                        "  • Update form handling to use Spring MVC conventions"
                    ])
                else:
                    report.extend([
                        f"  • Update {record['count']} HTML templates to use Thymeleaf syntax",
                        "  • Add Thymeleaf namespace to templates",
                        "  • Update static resource references"
                    ])

        return report

    def save_report(self, filename="migration_report.txt"):
        """Save the migration analysis and recommendations to a file"""
        report = self.analyze_project()
        
        with open(filename, 'w') as f:
            f.write("\n".join(report))
        
        print(f"Migration analysis report saved to {filename}")

if __name__ == "__main__":
    planner = MigrationPlanner("bolt://localhost:7687", "neo4j", "password")
    
    try:
        planner.save_report()
    finally:
        planner.close()
