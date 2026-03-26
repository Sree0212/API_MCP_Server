import json
import base64
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import configparser


class JiraService:

    def __init__(self, artefacts_base_path: str):
        self.artefacts_base_path = artefacts_base_path
        self.config_cache: Dict[str, Dict[str, str]] = {}

    # =========================================================
    # GET ISSUES UPDATED SINCE
    # =========================================================
    def get_issues_updated_since(self, project_name: str, last_polled: datetime) -> List[Dict]:

        config = self.get_jira_config(project_name)

        jira_url = config["jira_url"]
        auth_header = config["authHeader"]
        project_key = config["jira_project_key"]

        jql_timestamp = last_polled.strftime("%Y-%m-%d %H:%M")

        jql = f'project = {project_key} AND issueType = Story AND updated > "{jql_timestamp}" ORDER BY updated ASC'

        response = requests.post(
            f"{jira_url}/rest/api/3/search/jql",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            json={"jql": jql},
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Jira search failed: {response.status_code} {response.text}")

        data = response.json()
        stories = []

        for issue in data.get("issues", []):
            issue_id = issue.get("id")

            if issue_id:
                try:
                    story = self.get_issue_details(project_name, issue_id)
                    stories.append(story)
                except Exception as e:
                    print(f"Failed to fetch issue {issue_id}: {e}")

        return stories

    # =========================================================
    # GET ISSUE DETAILS
    # =========================================================
    def get_issue_details(self, project_name: str, issue_id: str) -> Dict:

        config = self.get_jira_config(project_name)

        jira_url = config["jira_url"]
        auth_header = config["authHeader"]

        response = requests.get(
            f"{jira_url}/rest/api/2/issue/{issue_id}",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json"
            },
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch issue {issue_id}: {response.status_code}")

        root = response.json()

        story = {
            "issueKey": root.get("key"),
            "summary": root.get("fields", {}).get("summary"),
            "description": root.get("fields", {}).get("description", ""),
        }

        try:
            updated = root.get("fields", {}).get("updated")
            story["lastUpdated"] = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%S.%f%z")
        except Exception:
            story["lastUpdated"] = datetime.now()

        return story

    # =========================================================
    # POST COMMENT
    # =========================================================
    def post_comment_to_issue(self, project_name: str, issue_key: str, comment_body: str):

        try:
            config = self.get_jira_config(project_name)

            jira_url = config["jira_url"]
            auth_header = config["authHeader"]

            payload = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment_body
                                }
                            ]
                        }
                    ]
                }
            }

            response = requests.post(
                f"{jira_url}/rest/api/3/issue/{issue_key}/comment",
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            )

            if response.status_code == 201:
                print(f"Comment posted to {issue_key}")
            else:
                print(f"Failed to post comment: {response.status_code} {response.text}")

        except Exception as e:
            print(f"Error posting comment: {e}")

    # =========================================================
    # CONFIG LOADER (CACHED)
    # =========================================================
    def get_jira_config(self, project_key: str) -> Dict[str, str]:

        if project_key in self.config_cache:
            return self.config_cache[project_key]

        config_path = Path(
            self.artefacts_base_path,
            "Main",
            project_key,
            "config",
            "config.ini"
        )

        if not config_path.exists():
            raise Exception(f"config.ini not found for project: {project_key}")

        parser = configparser.ConfigParser()
        parser.read(config_path)

        jira_url = parser.get("JIRA", "jira_url", fallback=None)
        jira_api_token = parser.get("JIRA", "jira_api_token", fallback=None)
        jira_project_key = parser.get("JIRA", "jira_project_key", fallback=None)
        jira_user = parser.get("JIRA", "jira_user", fallback=None)

        if not jira_url or not jira_api_token or not jira_project_key:
            raise Exception("Invalid Jira config")

        auth = f"{jira_user}:{jira_api_token}"
        auth_header = "Basic " + base64.b64encode(auth.encode()).decode()

        config = {
            "jira_url": jira_url,
            "authHeader": auth_header,
            "jira_project_key": jira_project_key
        }

        self.config_cache[project_key] = config
        return config


# =========================================================
# INIT FUNCTION (IMPORTANT FOR MCP)
# =========================================================
def init_jira_tool(artefacts_base_path: str):
    return JiraService(artefacts_base_path)