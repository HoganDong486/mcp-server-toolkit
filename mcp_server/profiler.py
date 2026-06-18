"""
Self-profiling and proactive behavior for MCP Server.

Tracks tool usage patterns and suggests optimizations.
"""
import time
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class ToolProfile:
    name: str
    call_count: int = 0
    total_latency_ms: float = 0.0
    error_count: int = 0
    last_used: float = 0.0
    avg_input_size: int = 0
    success_rate: float = 1.0

    def record_call(self, latency_ms: float, input_size: int, success: bool):
        self.call_count += 1
        self.total_latency_ms += latency_ms
        self.last_used = time.time()
        if not success:
            self.error_count += 1
        if self.call_count > 0:
            self.success_rate = 1.0 - (self.error_count / self.call_count)
            self.avg_input_size = max(self.avg_input_size, input_size)

    @property
    def avg_latency(self) -> float:
        return self.total_latency_ms / max(self.call_count, 1)


class Profiler:
    """
    Tracks tool usage patterns and suggests optimizations.
    """

    def __init__(self, storage_path: str = "./profile_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.tools: Dict[str, ToolProfile] = {}
        self.session_start = time.time()

    def register_tool(self, name: str):
        if name not in self.tools:
            self.tools[name] = ToolProfile(name=name)

    def record_call(self, tool_name: str, latency_ms: float, input_size: int, success: bool):
        if tool_name not in self.tools:
            self.register_tool(tool_name)
        self.tools[tool_name].record_call(latency_ms, input_size, success)

    def get_hot_tools(self, top_n: int = 5) -> List[Dict]:
        sorted_tools = sorted(self.tools.values(), key=lambda t: t.call_count, reverse=True)
        return [
            {
                "name": t.name,
                "calls": t.call_count,
                "avg_latency_ms": round(t.avg_latency, 2),
                "success_rate": round(t.success_rate, 3),
                "last_used_ago_s": round(time.time() - t.last_used, 1),
            }
            for t in sorted_tools[:top_n]
        ]

    def get_cold_tools(self) -> List[str]:
        return [name for name, t in self.tools.items() if t.call_count == 0]

    def suggest_improvements(self) -> List[Dict]:
        suggestions = []
        for name, t in self.tools.items():
            if t.error_count > 0 and t.call_count > 5 and t.success_rate < 0.8:
                suggestions.append({
                    "tool": name,
                    "issue": "high_error_rate",
                    "success_rate": round(t.success_rate, 3),
                    "suggestion": "Check input validation and add better error handling",
                })
            if t.avg_latency > 500 and t.call_count > 5:
                suggestions.append({
                    "tool": name,
                    "issue": "high_latency",
                    "avg_latency_ms": round(t.avg_latency, 2),
                    "suggestion": "Consider caching or optimizing this tool",
                })
        return suggestions

    def get_session_report(self) -> Dict:
        total_calls = sum(t.call_count for t in self.tools.values())
        total_errors = sum(t.error_count for t in self.tools.values())
        return {
            "session_duration_s": round(time.time() - self.session_start, 1),
            "total_tool_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": round(total_errors / max(total_calls, 1), 4),
            "tools_used": len([t for t in self.tools.values() if t.call_count > 0]),
            "tools_unused": len(self.get_cold_tools()),
            "top_tools": self.get_hot_tools(5),
            "improvement_suggestions": self.suggest_improvements(),
        }
