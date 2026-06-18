#!/usr/bin/env python3

from mcp_server.server import MCPServer
from mcp_server.tools.filesystem import FS_TOOLS
from mcp_server.tools.git_tools import GIT_TOOLS
from mcp_server.tools.database import DB_TOOLS


def main():
    server = MCPServer("mcp-toolkit", "1.0.0")

    for name, spec in FS_TOOLS.items():
        server.register_tool(name, spec["description"], spec["schema"], spec["handler"])

    for name, spec in GIT_TOOLS.items():
        server.register_tool(name, spec["description"], spec["schema"], spec["handler"])

    for name, spec in DB_TOOLS.items():
        server.register_tool(name, spec["description"], spec["schema"], spec["handler"])

    server.register_tool(
        "calculator",
        "Evaluate a mathematical expression",
        {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "Math expression (e.g. 1 + 2 * 3)"}},
            "required": ["expression"],
        },
        lambda args: {"content": str(eval(args["expression"], {"__builtins__": {}}, {}))}
        if len(args.get("expression", "")) < 200
        else {"content": "Expression too long"},
    )

    server.run()


if __name__ == "__main__":
    main()
