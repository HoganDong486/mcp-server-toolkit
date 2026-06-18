#!/usr/bin/env python3

import time
import json
from mcp_server.server import MCPServer
from mcp_server.tools.filesystem import FS_TOOLS
from mcp_server.tools.git_tools import GIT_TOOLS
from mcp_server.tools.database import DB_TOOLS
from mcp_server.profiler import Profiler


def wrap_with_profiling(handler, tool_name: str, profiler: Profiler):
    def wrapped(args: dict) -> dict:
        input_size = len(json.dumps(args))
        start = time.time()
        success = True
        try:
            result = handler(args)
        except Exception as e:
            success = False
            result = {"content": f"Error: {str(e)}"}
        latency = (time.time() - start) * 1000
        profiler.record_call(tool_name, latency, input_size, success)
        return result
    return wrapped


def main():
    profiler = Profiler()
    server = MCPServer("mcp-toolkit", "2.0.0")

    for name, spec in FS_TOOLS.items():
        server.register_tool(
            name, spec["description"], spec["schema"],
            wrap_with_profiling(spec["handler"], name, profiler),
        )

    for name, spec in GIT_TOOLS.items():
        server.register_tool(
            name, spec["description"], spec["schema"],
            wrap_with_profiling(spec["handler"], name, profiler),
        )

    for name, spec in DB_TOOLS.items():
        server.register_tool(
            name, spec["description"], spec["schema"],
            wrap_with_profiling(spec["handler"], name, profiler),
        )

    server.register_tool(
        "calculator",
        "Evaluate a mathematical expression",
        {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "Math expression (e.g. 1 + 2 * 3)"}},
            "required": ["expression"],
        },
        wrap_with_profiling(
            lambda args: {"content": str(eval(args["expression"], {"__builtins__": {}}, {}))}
            if len(args.get("expression", "")) < 200
            else {"content": "Expression too long"},
            "calculator", profiler,
        ),
    )

    server.register_tool(
        "session_stats",
        "Get session statistics: tools used, latency, error rates, and improvement suggestions",
        {"type": "object", "properties": {}, "required": []},
        lambda args: {"content": json.dumps(profiler.get_session_report(), indent=2, default=str)},
    )

    server.register_tool(
        "improvement_suggestions",
        "Get suggestions for improving tool reliability and performance",
        {"type": "object", "properties": {}, "required": []},
        lambda args: {"content": json.dumps(profiler.suggest_improvements(), indent=2) if profiler.suggest_improvements() else "No improvements needed"},
    )

    server.run()


if __name__ == "__main__":
    main()
