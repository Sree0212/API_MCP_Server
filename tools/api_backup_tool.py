import os
import shutil
from datetime import datetime
from pathlib import Path


class ApiBackupTool:

    def __init__(self, artefacts_base_path: str):
        self.artefacts_base_path = artefacts_base_path

    # =========================================================
    # CREATE BACKUP
    # =========================================================
    def create_backup(
        self,
        project_name: str,
        collection_id: str,
        file_name: str,
        source_file: str = None,   # optional (for flexibility like MCP usage)
    ) -> str:

        backups_dir = Path(
            self.artefacts_base_path,
            "Main",
            project_name,
            "api_discovery",
            "collections",
            collection_id,
            "backups",
        )

        backups_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_name = f"backup_{timestamp}_{file_name}"
        backup_path = backups_dir / backup_name

        # If source_file not passed → derive default path
        if source_file:
            source_path = Path(source_file)
        else:
            source_path = Path(
                self.artefacts_base_path,
                "Main",
                project_name,
                "api_discovery",
                "collections",
                collection_id,
                file_name,
            )

        if source_path.exists():
            shutil.copy(source_path, backup_path)
            return backup_name

        return None

    # =========================================================
    # RESTORE BACKUP
    # =========================================================
    def restore_backup(
        self,
        project_name: str,
        collection_id: str,
        backup_file_name: str,
        target_file: str,
    ):

        backups_dir = Path(
            self.artefacts_base_path,
            "Main",
            project_name,
            "api_discovery",
            "collections",
            collection_id,
            "backups",
        )

        backup_path = backups_dir / backup_file_name
        target_path = Path(target_file)

        if not backup_path.exists():
            raise Exception(f"Backup not found: {backup_file_name}")

        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy(backup_path, target_path)

        return {
            "message": f"Backup restored successfully",
            "backupFile": backup_file_name,
            "targetFile": str(target_path),
        }


# =========================================================
# MCP INIT
# =========================================================
def init_backup_tool(artefacts_base_path: str):
    return ApiBackupTool(artefacts_base_path)