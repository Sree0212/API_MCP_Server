import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import configparser


class JiraPollingService:

    def __init__(self, artefacts_base_path: str, jira_service, app_map_service, poll_interval: int = 300):
        self.artefacts_base_path = artefacts_base_path
        self.jira_service = jira_service
        self.app_map_service = app_map_service
        self.poll_interval = poll_interval  # seconds

        # Equivalent to ConcurrentHashMap
        self.last_polled_timestamps: Dict[str, datetime] = {}

        self.running = False

    # =========================================================
    # MAIN POLLING LOOP
    # =========================================================
    def start(self):
        print("Starting Jira Polling Agent...")
        self.running = True

        while self.running:
            try:
                self.poll_jira_projects()
            except Exception as e:
                print(f"Polling cycle failed: {e}")

            time.sleep(self.poll_interval)

    def stop(self):
        self.running = False

    # =========================================================
    # POLL ALL PROJECTS
    # =========================================================
    def poll_jira_projects(self):
        main_dir = Path(self.artefacts_base_path, "Main")

        if not main_dir.exists():
            print("Main directory not found!")
            return

        for project_dir in main_dir.iterdir():
            if project_dir.is_dir():
                project_name = project_dir.name

                jira_project_key = self.get_jira_project_key(project_name)

                if jira_project_key:
                    print(f"Polling Jira for project: {project_name} (Key: {jira_project_key})")

                    try:
                        self.process_project_updates(project_name)
                    except Exception as e:
                        print(f"Failed project {project_name}: {e}")

        print("Jira Polling cycle finished.\n")

    # =========================================================
    # PROCESS UPDATES
    # =========================================================
    def process_project_updates(self, project_name: str):

        last_poll = self.last_polled_timestamps.get(
            project_name,
            datetime.now() - timedelta(minutes=5)
        )

        current_poll_time = datetime.now()

        updated_issues = self.jira_service.get_issues_updated_since(
            project_name,
            last_poll
        )

        if not updated_issues:
            print(f"No updates for {project_name} since {last_poll}")
        else:
            print(f"Found {len(updated_issues)} updates for {project_name}")

            try:
                self.app_map_service.process_jira_issue_updates(
                    project_name,
                    updated_issues
                )
            except Exception as e:
                print(f"Processing failed for {project_name}: {e}")

        # update timestamp
        self.last_polled_timestamps[project_name] = current_poll_time

    # =========================================================
    # READ CONFIG.INI
    # =========================================================
    def get_jira_project_key(self, project_name: str) -> Optional[str]:

        config_path = Path(
            self.artefacts_base_path,
            "Main",
            project_name,
            "config",
            "config.ini"
        )

        if not config_path.exists():
            return None

        try:
            parser = configparser.ConfigParser()
            parser.read(config_path)

            return parser.get("JIRA", "jira_project_key", fallback=None)

        except Exception as e:
            print(f"Config read error for {project_name}: {e}")
            return None