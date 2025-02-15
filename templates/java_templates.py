"""Templates for Java source files"""

MODEL_TEMPLATE = """package {package};

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;
import jakarta.validation.constraints.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "{name_lower}s")
public class {name} {{
    @Id
    private String id;
    
{fields}
}}"""

REPOSITORY_TEMPLATE = """package {package};

import {model_package}.{model_name};
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {name} extends MongoRepository<{model_name}, String> {{
}}"""

SERVICE_TEMPLATE = """package {package};

import {model_package}.{model_name};
import {repository_package}.{model_name}Repository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class {name} {{
    @Autowired
    private {model_name}Repository repository;
    
    public List<{model_name}> findAll() {{
        return repository.findAll();
    }}
    
    public Optional<{model_name}> findById(String id) {{
        return repository.findById(id);
    }}
    
    public {model_name} save({model_name} entity) {{
        return repository.save(entity);
    }}
    
    public void deleteById(String id) {{
        repository.deleteById(id);
    }}
}}"""

CONTROLLER_TEMPLATE = """package {package};

import {model_package}.{model_name};
import {service_package}.{model_name}Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/{model_name_lower}s")
public class {name} {{
    @Autowired
    private {model_name}Service service;
    
    @GetMapping
    public ResponseEntity<List<{model_name}>> getAll() {{
        return ResponseEntity.ok(service.findAll());
    }}
    
    @GetMapping("/{{id}}")
    public ResponseEntity<{model_name}> getById(@PathVariable String id) {{
        return service.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }}
    
    @PostMapping
    public ResponseEntity<{model_name}> create(@Valid @RequestBody {model_name} entity) {{
        return ResponseEntity.ok(service.save(entity));
    }}
    
    @PutMapping("/{{id}}")
    public ResponseEntity<{model_name}> update(@PathVariable String id, @Valid @RequestBody {model_name} entity) {{
        return service.findById(id)
            .map(existing -> {{
                entity.setId(id);
                return ResponseEntity.ok(service.save(entity));
            }})
            .orElse(ResponseEntity.notFound().build());
    }}
    
    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> delete(@PathVariable String id) {{
        service.deleteById(id);
        return ResponseEntity.ok().build();
    }}
}}"""

MAIN_CLASS_TEMPLATE = """package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class MigrationApplication {
    public static void main(String[] args) {
        SpringApplication.run(MigrationApplication.class, args);
    }
}"""

POM_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.0</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>1.0.0</version>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-mongodb</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>"""

APPLICATION_PROPERTIES_TEMPLATE = """# MongoDB Configuration
spring.data.mongodb.host=localhost
spring.data.mongodb.port=27017
spring.data.mongodb.database=migrated_db

# Server Configuration
server.port=8080""" 