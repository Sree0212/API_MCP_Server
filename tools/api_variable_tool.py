import json
import re
from typing import Dict, Any
from models import ApiDataset, ApiCollection, ApiCapture
from tools.api_discovery_tool import ApiDiscoveryTool


class ApiVariableService:

    def __init__(self, api_discovery_service: ApiDiscoveryTool):
        self.api_discovery_service = api_discovery_service

    # =========================================================
    # SUBSTITUTE VARIABLES
    # =========================================================
    def substitute_variables(
        self,
        project_name: str,
        collection_id: str,
        original_dataset: ApiDataset
    ) -> ApiDataset:

        collection: ApiCollection = self.api_discovery_service.get_collection(
            project_name, collection_id
        )

        if not collection:
            return original_dataset

        variables: Dict[str, Any] = collection.variables or {}
        if not variables:
            return original_dataset

        # Convert dataset → JSON string
        dataset_json = json.dumps(original_dataset.to_dict())

        # Replace {{variable}}
        pattern = re.compile(r"\{\{([^}]+)}}")

        def replace(match):
            var_name = match.group(1).strip()
            return str(variables.get(var_name, match.group(0)))

        updated_json = pattern.sub(replace, dataset_json)

        # Convert back → ApiDataset
        return ApiDataset.from_dict(json.loads(updated_json))

    # =========================================================
    # EXTRACT VARIABLES FROM RESPONSE
    # =========================================================
    def extract_variables(
        self,
        project_name: str,
        collection_id: str,
        response_body: str,
        dataset: ApiDataset
    ):

        if not dataset.captures:
            return

        try:
            root_node = json.loads(response_body)
        except Exception:
            print("Cannot extract variables: Response is not valid JSON.")
            return

        collection: ApiCollection = self.api_discovery_service.get_collection(
            project_name, collection_id
        )

        if not collection:
            return

        if collection.variables is None:
            collection.variables = {}

        updated = False

        for capture in dataset.captures:
            json_path = capture.jsonPath
            var_name = capture.variableName

            if not json_path or not var_name:
                continue

            value = self._extract_value_by_path(root_node, json_path)

            if value is not None:
                collection.variables[var_name] = value
                updated = True
                print(f"Captured variable: {var_name} = {value}")

        if updated:
            self.api_discovery_service.save_collection(project_name, collection)

    # =========================================================
    # JSON PATH EXTRACTION
    # =========================================================
    def _extract_value_by_path(self, data: Dict, path: str):

        # Remove "$."
        if path.startswith("$."):
            path = path[2:]

        parts = path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return str(current) if current is not None else None