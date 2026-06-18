# MCP Server Toolkit

A **Model Context Protocol (MCP)** server that equips AI coding agents (Claude Code, Codex, Cursor, OpenCode, Gemini CLI) with filesystem, Git, database, and computation tools.

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) is an open standard that enables AI agents to securely interact with external tools and data sources. An MCP server speaks JSON-RPC 2.0 over stdio, exposing **tools**, **resources**, and **prompts** to any MCP-compatible client.

## Tools

### Filesystem
| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Write content to a file |
| `list_directory` | List directory contents |
| `file_info` | File/directory metadata |

### Git
| Tool | Description |
|------|-------------|
| `git_status` | Working tree status |
| `git_log` | Commit history |
| `git_diff` | Uncommitted changes |
| `git_branch` | List branches |
| `git_show` | Commit details |

### Database (SQLite)
| Tool | Description |
|------|-------------|
| `db_query` | Execute SQL (read/write) |
| `db_list_tables` | List all tables |
| `db_schema` | Show table schemas |

### Computation
| Tool | Description |
|------|-------------|
| `calculator` | Evaluate math expressions |

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure your AI agent (Claude Code example)
# Add to .mcp.json:
```

```json
{
  "mcpServers": {
    "toolkit": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/path/to/mcp-server-toolkit"
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SAFE_ROOTS` | Current directory | `;`-delimited paths filesystem tools can access |

## Architecture

```
AI Agent (Claude Code / Codex / Cursor)
    |
    | JSON-RPC 2.0 over stdio
    v
MCPServer
    ├── Filesystem Tools  (read, write, list)
    ├── Git Tools         (status, log, diff, branch, show)
    ├── Database Tools    (query, list tables, schema)
    └── Calculator        (safe eval)
```

## Tech Stack

- **Python 3.10+** — No external dependencies
- **JSON-RPC 2.0** — MCP protocol transport
- **sqlite3** — Built-in database support
- **Path security** — Tools are sandboxed to `MCP_SAFE_ROOTS`

---

### Part of the Hogan Dong Agent Stack

This project is the **tool belt** in a multi-agent platform:

> **[AgentForge](https://github.com/HoganDong486/agentforge)** can plug this toolkit directly via MCP, giving its agents filesystem, Git, and database access.
>
> Also: [Browser MCP](https://github.com/HoganDong486/opencode-browser-mcp) · [RAG Agent](https://github.com/HoganDong486/rag-research-agent) · [Agent Playground](https://github.com/HoganDong486/multi-agent-playground)
