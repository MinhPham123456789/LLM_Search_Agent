# Ultilise this standard
# https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/

def manage_tools(tools: list) -> dict:
    """Put a list of tools into a dictionary for agent usage

    Args:
        tools (list): list of tools to be used agent

    Returns:
        dict: a dictionary of tools to be used by agent
    """
    tool_dict = {}
    for tool in tools:
        tool_dict[tool.name] = tool
    return tool_dict
