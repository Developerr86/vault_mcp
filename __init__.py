"""
Vault 78 MCP Server — CLI Wrapper Architecture.

Interfaces with an Obsidian vault strictly by spawning subprocesses
to execute CLI commands. No embedded LLM, no REST API, no direct file I/O.
"""

__version__ = "0.2.0"
