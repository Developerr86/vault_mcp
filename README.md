# Vault 78 MCP Server

A Model Context Protocol (MCP) server that reads and writes Markdown files from the Vault 78 directory and answers questions using Gemini 2.0.

## Features

- List all Markdown files in the vault
- Read specific Markdown files
- Write/update Markdown files
- Search for content in the vault
- Ask questions about the vault content using Gemini 2.0
- Summarize files or the entire vault

## Setup

1. Install the required dependencies:

```bash
pip install mcp google-generativeai python-dotenv
```

2. Set up your Gemini API key:

   - Copy `.env.example` to `.env`
   - Add your Gemini API key to the `.env` file:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

3. Run the server:

```bash
python server.py
```

## Using with Claude Desktop or other MCP clients

This MCP server can be used with any MCP-compatible client, such as Claude Desktop:

1. Install the server in Claude Desktop:

```bash
mcp install server.py
```

2. Or run it in development mode:

```bash
mcp dev server.py
```

## Available Resources and Tools

### Resources

- `vault://files` - List all Markdown files in the vault
- `vault://{file_path}` - Get the content of a specific Markdown file

### Tools

- `write_file(file_path, content)` - Write or update a Markdown file
- `ask_question(question, file_path=None)` - Ask a question about the vault content
- `search_vault(query)` - Search for content in the vault
- `summarize_content(file_path=None)` - Summarize a file or the entire vault

## Examples

### Listing files

```
What files are available in the vault?
```

### Reading a file

```
Show me the content of BucketList.md
```

### Writing a file

```
Create a new file called "Meeting Notes.md" with the following content:
# Meeting Notes
- Discussed project timeline
- Assigned tasks to team members
- Next meeting scheduled for Friday
```

### Asking questions

```
What topics are covered in the Deep Learning tutorial files?
```

### Searching

```
Search for any mentions of "neural networks" in the vault
```

### Summarizing

```
Summarize the content of the entire vault
```

## License

MIT
