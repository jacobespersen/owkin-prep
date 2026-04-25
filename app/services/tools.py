from typing import Any

from anthropic.types import ToolParam

import app.services.data_loader as data_module

TOOL_DEFINITIONS: list[ToolParam] = [
    ToolParam(
        name="get_targets",
        description=(
            "Return a list of genes associated with a given cancer type. "
            "Use this when the user asks about genes involved in a specific cancer."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "cancer_name": {
                    "type": "string",
                    "description": (
                        "The cancer type to look up, e.g. 'lung', 'breast', 'prostate'."
                    ),
                }
            },
            "required": ["cancer_name"],
        },
    ),
    ToolParam(
        name="get_expressions",
        description=(
            "Return median expression values for a list of genes within a "
            "specific cancer type. Use this when the user asks about expression "
            "levels or median values of specific genes for a cancer."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "cancer_name": {
                    "type": "string",
                    "description": "The cancer type to look up expressions for.",
                },
                "genes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "List of gene names to look up expression values for."
                    ),
                },
            },
            "required": ["cancer_name", "genes"],
        },
    ),
]


ALLOWED_TOOLS = {t["name"] for t in TOOL_DEFINITIONS}


def execute_tool(name: str, tool_input: dict[str, Any]) -> Any:
    """Execute a tool by name, restricted to the allowlist."""
    if name not in ALLOWED_TOOLS:
        raise ValueError(f"Unknown tool '{name}'")
    func = getattr(data_module, name, None)
    if func is None:
        raise ValueError(f"Tool '{name}' not implemented")
    return func(**tool_input)


def build_system_prompt() -> str:
    """Build the system prompt including available cancer types."""
    cancers = data_module.get_available_cancers()
    cancer_list = ", ".join(cancers)
    return (
        "You are a helpful assistant for querying gene and cancer data. "
        "You have access to a dataset of genes associated with various "
        "cancer types and their median expression values.\n\n"
        f"Available cancer types in the dataset: {cancer_list}.\n\n"
        "When a user asks about genes for a cancer type, use get_targets. "
        "When they ask about expression values, first use get_targets to "
        "find the genes, then use get_expressions with the same cancer_name "
        "to get their values. Always pass the cancer_name to get_expressions "
        "so values are scoped correctly. "
        "Present results clearly and concisely for non-technical users."
    )
