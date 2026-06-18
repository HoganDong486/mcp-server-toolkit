import json
import sys
import traceback
from typing import Any, Callable

ToolFn = Callable[[dict[str, Any]], dict[str, Any]]


class MCPServer:
    def __init__(self, name: str = "mcp-toolkit", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: dict[str, dict] = {}
        self.resources: dict[str, dict] = {}

    def register_tool(self, name: str, description: str, input_schema: dict, handler: ToolFn):
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": handler,
        }

    def register_resource(self, uri_template: str, name: str, description: str, mine_type: str = "text/plain"):
        self.resources[uri_template] = {
            "uri": uri_template,
            "name": name,
            "description": description,
            "mimeType": mine_type,
        }

    def handle_request(self, req: dict) -> dict:
        method = req.get("method")
        req_id = req.get("id")
        params = req.get("params", {})

        try:
            if method == "initialize":
                return self._response(req_id, {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": self.name, "version": self.version},
                    "capabilities": {
                        "tools": {},
                        "resources": {"subscribe": False},
                    },
                })

            elif method == "tools/list":
                tools_list = [
                    {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
                    for t in self.tools.values()
                ]
                return self._response(req_id, {"tools": tools_list})

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                if tool_name not in self.tools:
                    return self._error(req_id, -32601, f"Tool not found: {tool_name}")
                result = self.tools[tool_name]["handler"](tool_args)
                content = result.get("content", str(result))
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                return self._response(req_id, {"content": content})

            elif method == "resources/list":
                return self._response(req_id, {
                    "resources": [
                        {"uri": r["uri"], "name": r["name"], "description": r["description"], "mimeType": r["mimeType"]}
                        for r in self.resources.values()
                    ]
                })

            elif method == "resources/read":
                uri = params.get("uri", "")
                if uri in self.resources:
                    return self._response(req_id, {
                        "contents": [{"uri": uri, "mimeType": self.resources[uri]["mimeType"], "text": f"Resource: {self.resources[uri]['name']}"}]
                    })
                return self._error(req_id, -32601, f"Resource not found: {uri}")

            elif method == "notifications/initialized":
                return None

            else:
                return self._error(req_id, -32601, f"Method not found: {method}")

        except Exception as e:
            return self._error(req_id, -32603, str(e))

    def _response(self, req_id, result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def _error(self, req_id, code: int, message: str):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

    def run(self):
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                req = json.loads(line.strip())
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                break
            except Exception:
                traceback.print_exc(file=sys.stderr)
                break
