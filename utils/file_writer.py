"""Utility for writing files"""

import os
from pathlib import Path

class FileWriter:
    def write_file(self, directory, filename, content):
        """
        Write content to a file in the specified directory
        
        Args:
            directory (str): Directory path where file should be created
            filename (str): Name of the file to create
            content (str): Content to write to the file
        """
        # Create directory if it doesn't exist
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create full file path
        file_path = os.path.join(directory, filename)
        
        # Write content to file
        with open(file_path, 'w') as f:
            f.write(content) 