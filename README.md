# Vault 78 MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that interfaces with an Obsidian vault **strictly by spawning subprocesses** to execute CLI commands. No embedded LLM, no REST API, no direct file I/O from Python.

## Requirements

### CLI Tool

The server requires a CLI tool capable of **search**, **read**, **write**, and **append** operations on vault files.

**Recommended (all four operations):** the official Obsidian CLI, enabled from Obsidian desktop **Settings → Community → CLI**. This makes the `obsidian` command available on your system `$PATH`.

Alternatives:

| Tool | Install | Search | Read | Write | Append |
|---|---|---|---|---|---|
| `obsidian` | Official Obsidian CLI (enabled in desktop app) | ✅ | ✅ | ✅ | ✅ |
| PowerShell (Windows) | Built into Windows | ✅ (via `findstr`) | ✅ | ✅ | ✅ |
| `rg` (ripgrep) | `winget install BurntSushi.ripgrep` | ✅ | ❌ | ❌ | ❌ |

Ensure the CLI tool is either in your system `$PATH` or provide the full path in the `.env` file.

## Setup

1. Install the required Python dependencies:

```bash
pip install mcp python-dotenv
```

2. Configure `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your vault path and CLI tool:

```env
VAULT_ABSOLUTE_PATH=C:\Users\YourName\Vault 78
OBSIDIAN_CLI_COMMAND=obsidian
```

3. Run the server:

```bash
python server.py
```

## Using with MCP Clients

### Option A: `mcp install` (auto-configures the client)

```bash
mcp install server.py
```

### Option B: Manual config.json entry

Add the following entry to your MCP client's config file (e.g. Claude Desktop's `claude_desktop_config.json`, or any client that follows the standard schema):

```json
{
  "mcpServers": {
    "vault-78": {
      "command": "python",
      "args": [
        "D:\\path\\to\\vault_mcp\\server.py"
      ],
      "env": {
        "VAULT_ABSOLUTE_PATH": "C:\\Users\\YourName\\Vault 78",
        "OBSIDIAN_CLI_COMMAND": "obsidian"
      }
    }
  }
}
```

> **Tip:** If you use `uvx`, replace `"command": "python"` with `"command": "uv"` and add `"run"` as the first `args` element.

## Available Tools

| Tool | Description |
|---|---|
| `search_vault(query, path=None)` | Search vault content via CLI grep. Narrow with optional path. |
| `read_note(file_path)` | Read the full content of a specific note. |
| `write_note(file_path, content)` | Create a new note or overwrite an existing one. |
| `append_to_note(file_path, content)` | Append text to the end of an existing note. |

## Security

- **No shell injection:** All user-supplied arguments are passed as safe argument lists to `subprocess`. `shell=True` is never used.
- **Path traversal prevention:** All file paths are resolved against the vault root and checked — any path escaping the vault (e.g. `../../../etc/shadow`) is rejected with a `PermissionError`.
- **Extension enforcement:** Only `.md` and `.canvas` files can be read or written.
- **Timeout safety:** All subprocess calls have a 30-second timeout.

## Examples

### Searching

```
Search for "neural networks" in the vault.
```

### Reading a note

```
Show me the content of Projects/Ideas.md
```

### Writing a note

```
Create a file called "Daily/2024-01-01.md" with the content:
# January 1, 2024
Started the new year with a fresh vault.
```

### Appending to a note

```
Add "- Buy groceries" to the end of Todo.md
```

## License

MIT
