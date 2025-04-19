"""
Markdown Processor module for the Vault 78 MCP Server.
Handles reading and writing Markdown files from the vault.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

class MarkdownProcessor:
    def __init__(self, vault_path: str):
        """
        Initialize the Markdown processor with the path to the vault directory.
        
        Args:
            vault_path (str): Path to the vault directory containing MD files
        """
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists() or not self.vault_path.is_dir():
            raise ValueError(f"Vault path '{vault_path}' does not exist or is not a directory")
    
    def get_all_files(self) -> List[Dict[str, str]]:
        """
        Get a list of all MD files in the vault.
        
        Returns:
            list: List of dictionaries with file information
        """
        md_files = []
        
        for root, dirs, files in os.walk(self.vault_path):
            # Skip .obsidian directory
            if '.obsidian' in dirs:
                dirs.remove('.obsidian')
                
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.vault_path)
                    md_files.append({
                        'filename': file,
                        'path': rel_path,
                        'full_path': full_path
                    })
        
        return md_files
    
    def read_file(self, file_path: str) -> Dict[str, str]:
        """
        Read the content of a specific MD file.
        
        Args:
            file_path (str): Path to the MD file relative to the vault
            
        Returns:
            dict: Dictionary with file content and metadata
        """
        full_path = self.vault_path / file_path
        
        if not full_path.exists() or not full_path.is_file():
            raise FileNotFoundError(f"File '{file_path}' not found in vault")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'filename': full_path.name,
            'path': file_path,
            'content': content
        }
    
    def write_file(self, file_path: str, content: str) -> bool:
        """
        Write content to a specific MD file.
        
        Args:
            file_path (str): Path to the MD file relative to the vault
            content (str): Content to write to the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        full_path = self.vault_path / file_path
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False
    
    def get_file_content_as_text(self, file_path: str) -> str:
        """
        Get the raw text content of a file.
        
        Args:
            file_path (str): Path to the MD file relative to the vault
            
        Returns:
            str: Raw text content of the file
        """
        file_data = self.read_file(file_path)
        return file_data['content']
    
    def get_all_content(self) -> str:
        """
        Get the content of all MD files in the vault.
        
        Returns:
            str: Combined content of all MD files
        """
        all_content = []
        
        for file_info in self.get_all_files():
            try:
                content = self.get_file_content_as_text(file_info['path'])
                all_content.append(f"# {file_info['filename']}\n\n{content}")
            except Exception as e:
                print(f"Error reading file {file_info['path']}: {e}")
        
        return "\n\n---\n\n".join(all_content)
    
    def search_content(self, query: str) -> List[Dict[str, str]]:
        """
        Search for content in the vault.
        
        Args:
            query (str): The search query
            
        Returns:
            list: List of dictionaries with search results
        """
        results = []
        
        for file_info in self.get_all_files():
            try:
                content = self.get_file_content_as_text(file_info['path'])
                
                # Case-insensitive search
                if re.search(query, content, re.IGNORECASE):
                    # Create a snippet with context
                    match = re.search(query, content, re.IGNORECASE)
                    if match:
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        snippet = content[start:end]
                        
                        # Add ellipsis if we're not at the beginning/end
                        if start > 0:
                            snippet = "..." + snippet
                        if end < len(content):
                            snippet = snippet + "..."
                        
                        results.append({
                            'path': file_info['path'],
                            'snippet': snippet
                        })
            except Exception as e:
                print(f"Error searching file {file_info['path']}: {e}")
        
        return results
