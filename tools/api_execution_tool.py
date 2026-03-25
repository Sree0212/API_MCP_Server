from pathlib import Path
from typing import Optional
from tools.api_variable_tool import ApiVariableService
from tools.api_intelligence_tool import ApiIntelligenceTool
from tools.api_discovery_tool import ApiDiscoveryTool
from tools.api_backup_tool import ApiBackupTool
from tools.llm_service import LLMService

class ApiExecutionTool:
    """
    Main execution tool for MCP APIs.
    Handles dependencies and API execution flow.
    """

    def __init__(self, artefacts_base_path: str):
        # Initialize dependencies (like dependency injection)
        self.discovery_service = ApiDiscoveryTool(artefacts_base_path)
        self.variable_service = ApiVariableService(self.discovery_service)
        self.backup_service = ApiBackupTool(artefacts_base_path)
        self.llm_service = LLMService()
        self.intelligence_service = ApiIntelligenceTool(artefacts_base_path)

    # =========================================================
    # MCP TOOL METHOD
    # =========================================================
    def execute_api(
        self,
        project_name: str,
        collection_id: str,
        endpoint_id: str,
        dataset_id: str,
        base_url_override: Optional[str] = None,
        auto_heal: bool = False,
        analyze_flows: bool = False,
        capture_response: bool = False,
        alternate_path: Optional[str] = None
    ):
        """
        Full execution flow for an API call.
        """
        alt_path = Path(alternate_path) if alternate_path else None

        # Call the internal execution logic
        return self._execute_api_core(
            project_name,
            collection_id,
            endpoint_id,
            dataset_id,
            base_url_override,
            auto_heal,
            analyze_flows,
            capture_response,
            alt_path
        )

    # =========================================================
    # INTERNAL EXECUTION LOGIC
    # =========================================================
    def _execute_api_core(
        self,
        project_name: str,
        collection_id: str,
        endpoint_id: str,
        dataset_id: str,
        base_url_override,
        auto_heal,
        analyze_flows,
        capture_response,
        alt_path
    ):
        """
        Internal logic for executing the API.
        Replace this with your actual API call flow.
        """
        print(f"[MCP] Executing API for project: {project_name}")
        print(f"[MCP] Collection: {collection_id}, Endpoint: {endpoint_id}, Dataset: {dataset_id}")
        print(f"[MCP] Options -> auto_heal: {auto_heal}, analyze_flows: {analyze_flows}, capture_response: {capture_response}")
        if alt_path:
            print(f"[MCP] Using alternate path: {alt_path}")

        # Example return structure, replace with real results
        return {
            "project": project_name,
            "collection": collection_id,
            "endpoint": endpoint_id,
            "dataset": dataset_id,
            "status": "success"
        }


# =========================================================
# MCP INIT FUNCTION
# =========================================================
def init_execution_tool(artefacts_base_path: str) -> ApiExecutionTool:
    """
    Factory function to initialize the MCP execution tool.
    """
    return ApiExecutionTool(artefacts_base_path)