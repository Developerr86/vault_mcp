#!/usr/bin/env python3
"""
Vault 78 MCP Server - A Model Context Protocol server that reads and writes Markdown files
from the Vault 78 directory and answers questions using Gemini 2.0.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv

# Import our modules
from markdown_processor import MarkdownProcessor
from gemini_service import GeminiService

# Load environment variables
load_dotenv()

# Check for required environment variables
if not os.getenv("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY environment variable is not set.")
    print("Please set it in a .env file or export it in your environment.")
    sys.exit(1)

# Initialize the MCP server
mcp = FastMCP("Vault 78 MCP Server")

# Initialize our services
VAULT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Vault 78"))
md_processor = MarkdownProcessor(VAULT_PATH)
gemini_service = GeminiService()

# Resource to list all markdown files
@mcp.resource("vault://files")
def list_files() -> str:
    """List all markdown files in the vault."""
    files = md_processor.get_all_files()
    if not files:
        return "No markdown files found in the vault."
    
    result = "# Markdown Files in Vault 78\n\n"
    for file in files:
        result += f"- [{file['path']}](vault://{file['path']})\n"
    
    return result

# Resource to get a specific markdown file
@mcp.resource("vault://{file_path}")
def get_file(file_path: str) -> str:
    """Get the content of a specific markdown file."""
    try:
        file_data = md_processor.read_file(file_path)
        return file_data["content"]
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found in the vault."
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Tool to write/update a markdown file
@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write or update a markdown file in the vault.
    
    Args:
        file_path: Path to the file relative to the vault root
        content: Content to write to the file
    
    Returns:
        Success or error message
    """
    try:
        # Ensure the file has .md extension
        if not file_path.endswith('.md'):
            file_path += '.md'
            
        success = md_processor.write_file(file_path, content)
        if success:
            return f"Successfully wrote to file: {file_path}"
        else:
            return f"Failed to write to file: {file_path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

# Tool to ask questions about the vault content
@mcp.tool()
def ask_question(question: str, file_path: Optional[str] = None) -> str:
    """
    Ask a question about the vault content using Gemini 2.0.
    
    Args:
        question: The question to ask
        file_path: Optional path to a specific file to use as context
    
    Returns:
        Gemini's response to the question
    """
    try:
        # Get context from specific file or all files
        if file_path:
            try:
                context = md_processor.get_file_content_as_text(file_path)
            except FileNotFoundError:
                return f"Error: File '{file_path}' not found in the vault."
        else:
            # Use all content as context
            context = md_processor.get_all_content()
        
        # Ask Gemini
        answer = gemini_service.ask_question(question, context)
        return answer
    except Exception as e:
        return f"Error asking question: {str(e)}"

# Tool to search for content in the vault
@mcp.tool()
def search_vault(query: str) -> str:
    """
    Search for content in the vault.
    
    Args:
        query: The search query
    
    Returns:
        Search results
    """
    try:
        results = md_processor.search_content(query)
        if not results:
            return f"No results found for query: '{query}'"
        
        result_text = f"# Search Results for '{query}'\n\n"
        for result in results:
            result_text += f"## [{result['path']}](vault://{result['path']})\n\n"
            result_text += f"{result['snippet']}\n\n"
        
        return result_text
    except Exception as e:
        return f"Error searching vault: {str(e)}"

# Tool to summarize a file or the entire vault
@mcp.tool()
def summarize_content(file_path: Optional[str] = None) -> str:
    """
    Summarize a file or the entire vault using Gemini 2.0.
    
    Args:
        file_path: Optional path to a specific file to summarize
    
    Returns:
        Summary of the content
    """
    try:
        # Get content from specific file or all files
        if file_path:
            try:
                content = md_processor.get_file_content_as_text(file_path)
                title = f"Summary of {file_path}"
            except FileNotFoundError:
                return f"Error: File '{file_path}' not found in the vault."
        else:
            # Use all content
            content = md_processor.get_all_content()
            title = "Summary of Vault 78"
        
        # Ask Gemini to summarize
        summary = gemini_service.summarize_content(content)
        return f"# {title}\n\n{summary}"
    except Exception as e:
        return f"Error summarizing content: {str(e)}"

if __name__ == "__main__":
    print(f"Starting Vault 78 MCP Server...")
    print(f"Vault path: {VAULT_PATH}")
    
    # Check if the vault path exists
    if not os.path.exists(VAULT_PATH):
        print(f"Error: Vault path '{VAULT_PATH}' does not exist.")
        sys.exit(1)
    
    # Run the server
    mcp.run()
