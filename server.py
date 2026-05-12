#!/usr/bin/env python3
"""
Vault 78 MCP Server — CLI Wrapper Architecture.

Interfaces with an Obsidian vault strictly by spawning subprocesses
to execute CLI commands. No embedded LLM, no REST API, no direct file I/O.
"""

import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from cli_wrapper import CliWrapper

load_dotenv()

mcp = FastMCP("Vault 78 MCP Server")
wrapper = CliWrapper()


@mcp.tool()
async def search_vault(query: str, path: str | None = None) -> str:
    """Search the Obsidian vault using local CLI search/grep.
    Use this to locate relevant files before reading them.

    Args:
        query: The search term or regex pattern
        path: Optional subdirectory or file path to narrow the search (relative to vault root)
    """
    try:
        result = await wrapper.search_vault(query, path)
        return result if result.strip() else f"No results found for query: '{query}'"
    except Exception as e:
        return f"Search failed: {e}"


@mcp.tool()
async def read_note(file_path: str) -> str:
    """Read the full markdown content of a specific note.
    Requires the exact file path relative to the vault root.

    Args:
        file_path: Path to the file relative to vault root (e.g. 'Daily/2024-01-01.md')
    """
    try:
        return await wrapper.read_file(file_path)
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found in the vault."
    except Exception as e:
        return f"Error reading file: {e}"


@mcp.tool()
async def write_note(file_path: str, content: str) -> str:
    """Create a new note or overwrite an existing one.

    Args:
        file_path: Path to the file relative to vault root (e.g. 'Projects/notes.md')
        content: Full markdown content to write
    """
    try:
        if not file_path.endswith(('.md', '.canvas')):
            file_path += '.md'
        await wrapper.write_file(file_path, content)
        return f"Successfully wrote to: {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"


@mcp.tool()
async def append_to_note(file_path: str, content: str) -> str:
    """Add text to the end of an existing note.

    Args:
        file_path: Path to the file relative to vault root
        content: Content to append
    """
    try:
        await wrapper.append_file(file_path, content)
        return f"Successfully appended to: {file_path}"
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found in the vault."
    except Exception as e:
        return f"Error appending to file: {e}"


if __name__ == "__main__":
    print("Starting Vault 78 MCP Server...")
    print(f"Vault path: {wrapper.vault_path}")
    print(f"CLI command: {' '.join(wrapper.cli_args)}")

    if not wrapper.vault_path.exists():
        print(f"Error: Vault path '{wrapper.vault_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    mcp.run()
