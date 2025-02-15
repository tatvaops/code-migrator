"""Templates for generating model classes"""

def get_model_template(package_name):
    return f"""package {package_name}.models;

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
@Document(collection = "{{name.lower()}}s")
public class {{name}} {{
    @Id
    private String id;
    
    {{fields}}
}}
"""

def get_repository_template(package_name):
    return f"""package {package_name}.repositories;

import {package_name}.models.{{model_name}};
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {{name}} extends MongoRepository<{{model_name}}, String> {{
}}
"""

def get_service_template(package_name):
    return f"""package {package_name}.services;

import {package_name}.models.{{model_name}};
import {package_name}.repositories.{{model_name}}Repository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class {{name}} {{
    @Autowired
    private {{model_name}}Repository repository;
    
    public List<{{model_name}}> findAll() {{
        return repository.findAll();
    }}
    
    public Optional<{{model_name}}> findById(String id) {{
        return repository.findById(id);
    }}
    
    public {{model_name}} save({{model_name}} entity) {{
        return repository.save(entity);
    }}
    
    public void deleteById(String id) {{
        repository.deleteById(id);
    }}
}}
"""

def get_controller_template(package_name):
    return f"""package {package_name}.controllers;

import {package_name}.models.{{model_name}};
import {package_name}.services.{{model_name}}Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/{{model_name.lower()}}s")
public class {{name}} {{
    @Autowired
    private {{model_name}}Service service;
    
    @GetMapping
    public ResponseEntity<List<{{model_name}}>> getAll() {{
        return ResponseEntity.ok(service.findAll());
    }}
    
    @GetMapping("/{{{{id}}}}")
    public ResponseEntity<{{model_name}}> getById(@PathVariable String id) {{
        return service.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }}
    
    @PostMapping
    public ResponseEntity<{{model_name}}> create(@Valid @RequestBody {{model_name}} entity) {{
        return ResponseEntity.ok(service.save(entity));
    }}
    
    @PutMapping("/{{{{id}}}}")
    public ResponseEntity<{{model_name}}> update(@PathVariable String id, @Valid @RequestBody {{model_name}} entity) {{
        return service.findById(id)
            .map(existing -> {{
                entity.setId(id);
                return ResponseEntity.ok(service.save(entity));
            }})
            .orElse(ResponseEntity.notFound().build());
    }}
    
    @DeleteMapping("/{{{{id}}}}")
    public ResponseEntity<Void> delete(@PathVariable String id) {{
        service.deleteById(id);
        return ResponseEntity.ok().build();
    }}
}}
""" 