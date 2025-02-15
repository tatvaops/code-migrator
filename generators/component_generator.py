"""Generator for Spring Boot components"""

import os
from pathlib import Path
from templates.java_templates import *

class ComponentGenerator:
    def __init__(self, file_writer):
        self.file_writer = file_writer
        self.base_package = "com.example.demo"  # Changed base package to demo
        
    def _get_package_name(self, component_type):
        """Get the full package name for a component type"""
        return f"{self.base_package}.{component_type}"
        
    def create_model(self, name, columns, base_path):
        fields = self._generate_fields(columns)
        content = MODEL_TEMPLATE.format(
            package=self._get_package_name("models"),
            name=name,
            name_lower=name.lower(),
            fields=fields
        )
        directory = os.path.join(base_path, "models")
        filename = f"{name}.java"
        self.file_writer.write_file(directory, filename, content)
        
    def create_repository(self, name, model_name, base_path):
        content = REPOSITORY_TEMPLATE.format(
            package=self._get_package_name("repositories"),
            model_package=self._get_package_name("models"),
            name=name,
            model_name=model_name
        )
        directory = os.path.join(base_path, "repositories")
        filename = f"{name}.java"
        self.file_writer.write_file(directory, filename, content)
        
    def create_service(self, name, model_name, base_path):
        content = SERVICE_TEMPLATE.format(
            package=self._get_package_name("services"),
            model_package=self._get_package_name("models"),
            repository_package=self._get_package_name("repositories"),
            name=name,
            model_name=model_name
        )
        directory = os.path.join(base_path, "services")
        filename = f"{name}.java"
        self.file_writer.write_file(directory, filename, content)
        
    def create_controller(self, name, model_name, columns, base_path):
        content = CONTROLLER_TEMPLATE.format(
            package=self._get_package_name("controllers"),
            model_package=self._get_package_name("models"),
            service_package=self._get_package_name("services"),
            name=name,
            model_name=model_name,
            model_name_lower=model_name.lower()
        )
        directory = os.path.join(base_path, "controllers")
        filename = f"{name}.java"
        self.file_writer.write_file(directory, filename, content)
        
    def create_pom_xml(self, target_dir):
        self.file_writer.write_file(target_dir, "pom.xml", POM_XML_TEMPLATE)
        
    def create_application_properties(self, target_dir):
        resources_dir = os.path.join(target_dir, "src/main/resources")
        Path(resources_dir).mkdir(parents=True, exist_ok=True)
        self.file_writer.write_file(resources_dir, "application.properties", APPLICATION_PROPERTIES_TEMPLATE)
        
    def create_main_class(self, base_path):
        self.file_writer.write_file(base_path, "MigrationApplication.java", MAIN_CLASS_TEMPLATE)
        
    def _generate_fields(self, columns):
        field_templates = []
        for column in columns:
            if column["name"] and column["type"]:
                constraints = column.get("constraints", [])
                annotations = []
                
                if "NotNull" in constraints:
                    annotations.append("@NotNull")
                if "Email" in constraints:
                    annotations.append("@Email")
                if "Size" in constraints:
                    annotations.append("@Size(max = 255)")  # Default size
                if "Column" in constraints:
                    annotations.append("@Indexed")
                
                annotation_str = "\n    ".join(annotations) + "\n    " if annotations else "    "
                field_templates.append(f"{annotation_str}private {column['type']} {column['name']};")
        
        return "\n    ".join(field_templates) 