import os

def get_namespace() -> str:
    """Get the base namespace from environment variable"""
    namespace = os.getenv('PACKAGE_NAMESPACE', "com.mongodb.kitchensink.demo")
    if not namespace:
        print("⚠️  PACKAGE_NAMESPACE not set, using default 'com.example.application'")
        return "com.example.application"
    return namespace

def get_package_declaration(file_type: str) -> str:
    """Get the full package declaration based on file type"""
    base_namespace = get_namespace()
    
    # Map file types to their package suffixes
    package_suffixes = {
        "Controller": "controller",
        "Service": "service",
        "Repository": "repository",
        "Entity": "model",
        "Config": "config",
        "Exception": "exception",
        "Util": "util"
    }
    
    suffix = package_suffixes.get(file_type, "")
    if suffix:
        return f"package {base_namespace}.{suffix};"
    return f"package {base_namespace};" 