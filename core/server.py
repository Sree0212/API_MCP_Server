from tools.api_discovery_tool import init_discovery_tool
from tools.api_execution_tool import init_execution_tool
from tools.api_intelligence_tool import init_intelligence_tool
from tools.api_backup_tool import init_backup_tool
from tools.llm_service import LLMService


class MCPServer:

    def __init__(self, artefacts_base_path: str):
        self.artefacts_base_path = artefacts_base_path

        # Initialize all tools
        self.discovery_tool = init_discovery_tool(artefacts_base_path)
        self.execution_tool = init_execution_tool(artefacts_base_path)
        self.intelligence_tool = init_intelligence_tool(artefacts_base_path)
        self.backup_tool = init_backup_tool(artefacts_base_path)
        self.llm_tool = LLMTool()


# Singleton-style init (like Spring context)
_server_instance = None


def get_server(artefacts_base_path: str = "artefacts") -> MCPServer:
    global _server_instance

    if _server_instance is None:
        _server_instance = MCPServer(artefacts_base_path)

    return _server_instance