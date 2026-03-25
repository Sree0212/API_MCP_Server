import json
from typing import Dict, Any, List

from models.api_heal_proposal import ApiHealProposal
from models.api_heal_action import ApiHealAction
from tools.api_discovery_tool import ApiDiscoveryTool
from tools.api_backup_tool import ApiBackupTool
from tools.llm_service import LLMService


class ApiIntelligenceTool:

    def __init__(self, artefacts_base_path: str):
        self.artefacts_base_path = artefacts_base_path

        # Tool dependencies (NOT services anymore)
        self.discovery_tool = ApiDiscoveryTool(artefacts_base_path)
        self.backup_tool = ApiBackupTool(artefacts_base_path)
        self.llm_tool = LLMService()

    # =========================================================
    # ANALYZE FAILURE (AI)
    # =========================================================
    def analyze_failure(
        self,
        endpoint: Dict,
        dataset: Dict,
        status_code: int,
        response_body: str,
    ) -> Dict:

        prompt = f"""
You are an API Debugger.

API FAILED.

Context:
- Method: {endpoint.get("method")}
- Path: {endpoint.get("path")}
- Request Data: {json.dumps(dataset)}
- Status Code: {status_code}
- Response Body: {response_body}

Task:
Identify the issue and suggest fixes.

Return ONLY JSON:
{{
  "diagnosis": "...",
  "actions": [
    {{
      "actionType": "UPDATE_METHOD | ADD_HEADER_DEF | SET_HEADER_VAL | SET_PARAM_VAL | UPDATE_BODY",
      "target": "ENDPOINT | DATASET",
      "key": "...",
      "value": "...",
      "reason": "..."
    }}
  ]
}}
"""

        try:
            raw = self.llm_tool.generate(prompt)
            clean = self._clean_json(raw)

            return json.loads(clean)

        except Exception as e:
            return {"error": str(e)}

    # =========================================================
    # APPLY FIX (CRITICAL FLOW)
    # =========================================================
    def apply_fix(
        self,
        project_name: str,
        collection_id: str,
        endpoint_id: str,
        dataset_id: str,
        proposal: Dict,
    ) -> Dict:

        # 1. Load data
        collection = self.discovery_tool.get_collection(project_name, collection_id)
        datasets = self.discovery_tool.get_datasets(project_name, collection_id, endpoint_id)

        endpoint = self._find_endpoint(collection, endpoint_id)
        dataset = next(ds for ds in datasets if ds["id"] == dataset_id)

        # 2. Backup BEFORE changes
        ds_backup = self.backup_tool.create_backup(
            project_name,
            collection_id,
            f"dataset_{endpoint_id}.json",
        )

        col_backup = self.backup_tool.create_backup(
            project_name,
            collection_id,
            f"collection_{collection_id}.json",
        )

        # 3. Apply actions
        for action in proposal.get("actions", []):
            target = action.get("target")

            if target == "ENDPOINT":
                self._apply_endpoint_change(endpoint, action)

            elif target == "DATASET":
                self._apply_dataset_change(dataset, action)

        # 4. Save updates
        self.discovery_tool.save_collection(project_name, collection)
        self.discovery_tool.save_datasets(project_name, collection_id, endpoint_id, datasets)

        return {
            "message": "Fix applied successfully",
            "backups": {
                "collection": col_backup,
                "dataset": ds_backup,
            },
            "updatedEndpoint": endpoint,
            "updatedDataset": dataset,
        }

    # =========================================================
    # CLEAR DIAGNOSIS
    # =========================================================
    def clear_diagnosis(self, project_name: str, collection_id: str, endpoint_id: str):

        collection = self.discovery_tool.get_collection(project_name, collection_id)
        endpoint = self._find_endpoint(collection, endpoint_id)

        if endpoint:
            endpoint["latestDiagnosis"] = None
            self.discovery_tool.save_collection(project_name, collection)

    # =========================================================
    # SUCCESS FLOW ANALYSIS (AI)
    # =========================================================
    def analyze_success(
        self,
        project_name: str,
        collection_id: str,
        source_endpoint_id: str,
        response_body: str,
    ) -> List[Dict]:

        try:
            collection = self.discovery_tool.get_collection(project_name, collection_id)

            candidates = ""
            for group in collection.get("groups", []):
                for ep in group.get("endpoints", []):
                    if ep["id"] != source_endpoint_id:
                        candidates += f'{ep["id"]}: {ep["method"]} {ep["path"]}\n'

            prompt = f"""
You are a Data Mapper.

Response:
{response_body}

Candidate APIs:
{candidates}

Find dependencies.

Return JSON:
[
  {{
    "targetId": "...",
    "parameterName": "...",
    "relationshipType": "DATA_FLOW"
  }}
]
"""

            raw = self.llm_tool.generate(prompt)
            clean = self._clean_json(raw)

            return json.loads(clean)

        except Exception:
            return []

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _apply_endpoint_change(self, endpoint: Dict, action: Dict):

        action_type = action.get("actionType")

        if action_type == "UPDATE_METHOD":
            endpoint["method"] = action.get("value")

        elif action_type == "ADD_HEADER_DEF":
            headers = endpoint.setdefault("headers", [])
            headers.append({
                "name": action.get("key"),
                "type": "string",
                "required": True
            })

    def _apply_dataset_change(self, dataset: Dict, action: Dict):

        action_type = action.get("actionType")

        if action_type == "SET_HEADER_VAL":
            dataset.setdefault("headers", {})[action.get("key")] = action.get("value")

        elif action_type == "SET_PARAM_VAL":
            dataset.setdefault("pathParams", {})[action.get("key")] = action.get("value")

        elif action_type == "UPDATE_BODY":
            dataset["body"] = action.get("value")

    def _find_endpoint(self, collection: Dict, endpoint_id: str):

        for group in collection.get("groups", []):
            for ep in group.get("endpoints", []):
                if ep["id"] == endpoint_id:
                    return ep
        return None

    def _clean_json(self, text: str):

        if "```json" in text:
            return text.split("```json")[1].split("```")[0]

        if "```" in text:
            return text.split("```")[1]

        return text


# =========================================================
# MCP INIT
# =========================================================
def init_intelligence_tool(artefacts_base_path: str):
    return ApiIntelligenceTool(artefacts_base_path)