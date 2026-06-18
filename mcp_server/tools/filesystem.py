import os
from pathlib import Path

SAFE_ROOTS = set(os.environ.get("MCP_SAFE_ROOTS", os.getcwd()).split(os.pathsep))


def _resolve(path: str) -> str:
    p = Path(path).resolve()
    for root in SAFE_ROOTS:
        if str(p).startswith(str(Path(root).resolve())):
            return str(p)
    raise PermissionError(f"Path {path} is outside allowed roots: {SAFE_ROOTS}")


def read_file(args: dict) -> dict:
    path = _resolve(args["path"])
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content}


def write_file(args: dict) -> dict:
    path = _resolve(args["path"])
    content = args["content"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"content": f"Written {len(content)} bytes to {path}"}


def list_directory(args: dict) -> dict:
    path = _resolve(args.get("path", "."))
    entries = []
    with os.scandir(path) as it:
        for entry in sorted(it, key=lambda e: (not e.is_dir(), e.name.lower())):
            prefix = "[DIR] " if entry.is_dir() else "[FILE]"
            entries.append(f"{prefix} {entry.name}")
    return {"content": "\n".join(entries) if entries else "(empty directory)"}


def file_info(args: dict) -> dict:
    path = _resolve(args["path"])
    stat = os.stat(path)
    info = {
        "path": path,
        "size_bytes": stat.st_size,
        "is_dir": os.path.isdir(path),
        "is_file": os.path.isfile(path),
        "modified": stat.st_mtime,
    }
    return {"content": "\n".join(f"{k}: {v}" for k, v in info.items())}


FS_TOOLS = {
    "read_file": {
        "description": "Read the contents of a file",
        "schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path to the file"}},
            "required": ["path"],
        },
        "handler": read_file,
    },
    "write_file": {
        "description": "Write content to a file (creates directories if needed)",
        "schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
        "handler": write_file,
    },
    "list_directory": {
        "description": "List contents of a directory",
        "schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Directory path (defaults to cwd)"}},
        },
        "handler": list_directory,
    },
    "file_info": {
        "description": "Get metadata about a file or directory",
        "schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path to the file"}},
            "required": ["path"],
        },
        "handler": file_info,
    },
}
