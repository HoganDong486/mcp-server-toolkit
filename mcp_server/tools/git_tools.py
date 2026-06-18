import subprocess
from pathlib import Path


def _run_git(args: list[str], cwd: str = None) -> str:
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd or Path.cwd(),
    )
    if result.returncode != 0:
        return f"Git error: {result.stderr.strip()}"
    return result.stdout.strip() or "(no output)"


def git_status(args: dict) -> dict:
    path = args.get("path", ".")
    output = _run_git(["status", "--short"], str(Path(path).resolve()))
    return {"content": output}


def git_log(args: dict) -> dict:
    path = args.get("path", ".")
    n = args.get("count", 10)
    output = _run_git(["log", f"-{n}", "--oneline", "--decorate"], str(Path(path).resolve()))
    return {"content": output}


def git_diff(args: dict) -> dict:
    path = args.get("path", ".")
    staged = args.get("staged", False)
    cmd = ["diff"]
    if staged:
        cmd.append("--staged")
    output = _run_git(cmd, str(Path(path).resolve()))
    return {"content": output[:4000] if len(output) > 4000 else output}


def git_branch(args: dict) -> dict:
    path = args.get("path", ".")
    output = _run_git(["branch", "-a"], str(Path(path).resolve()))
    return {"content": output}


def git_show(args: dict) -> dict:
    path = args.get("path", ".")
    ref = args.get("ref", "HEAD")
    output = _run_git(["show", "--stat", ref], str(Path(path).resolve()))
    return {"content": output[:4000] if len(output) > 4000 else output}


GIT_TOOLS = {
    "git_status": {
        "description": "Show the working tree status (git status --short)",
        "schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path to git repo (defaults to cwd)"}},
        },
        "handler": git_status,
    },
    "git_log": {
        "description": "Show commit logs",
        "schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to git repo"},
                "count": {"type": "integer", "description": "Number of commits (default 10)", "default": 10},
            },
        },
        "handler": git_log,
    },
    "git_diff": {
        "description": "Show changes between working tree and index (or HEAD)",
        "schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to git repo"},
                "staged": {"type": "boolean", "description": "Show staged changes instead"},
            },
        },
        "handler": git_diff,
    },
    "git_branch": {
        "description": "List branches",
        "schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path to git repo"}},
        },
        "handler": git_branch,
    },
    "git_show": {
        "description": "Show details of a commit (with stat)",
        "schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to git repo"},
                "ref": {"type": "string", "description": "Git ref (commit hash, branch, tag)", "default": "HEAD"},
            },
        },
        "handler": git_show,
    },
}
