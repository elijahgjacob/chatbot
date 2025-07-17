import sys
import types

# ----------------- tools stub -----------------

def _tool(name: str, return_direct: bool = False):
    """Mimic the @tool decorator from LangChain. Adds a simple .invoke helper."""
    def decorator(func):
        # Attach a naive invoke helper for easier mocking in tests
        def _invoke(params=None):  # type: ignore
            if params is None:
                return func()
            if isinstance(params, dict):
                # Pass dict as kwargs if function expects keywords
                try:
                    return func(**params)  # type: ignore[arg-type]
                except TypeError:
                    # Fallback: pass the dict as a single positional argument
                    return func(params)  # type: ignore[arg-type]
            return func(params)  # type: ignore[arg-type]
        func.invoke = _invoke  # type: ignore[attr-defined]
        return func
    return decorator

_tools_module = types.ModuleType("langchain.tools")
_tools_module.tool = _tool  # type: ignore[attr-defined]

# ----------------- schema stub -----------------

class _BaseMessage:
    def __init__(self, content: str):
        self.content = content

class HumanMessage(_BaseMessage):
    pass

class SystemMessage(_BaseMessage):
    pass

_schema_module = types.ModuleType("langchain.schema")
_schema_module.HumanMessage = HumanMessage  # type: ignore[attr-defined]
_schema_module.SystemMessage = SystemMessage  # type: ignore[attr-defined]

# Register the sub-modules so "from langchain.tools import tool" works
sys.modules["langchain.tools"] = _tools_module
sys.modules["langchain.schema"] = _schema_module

# Expose common attributes at package level
__all__ = [
    "tools",
    "schema",
]