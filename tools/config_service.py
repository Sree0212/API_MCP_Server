from pathlib import Path
from typing import Dict, List
import threading


# =========================================================
# USER MODEL
# =========================================================
class User:
    def __init__(self, username: str, password: str, role: str):
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            "username": self.username,
            "role": self.role
        }


# =========================================================
# CONFIG SERVICE
# =========================================================
class ConfigService:

    def __init__(self, artefacts_base_path: str):
        self.artefacts_base_path = artefacts_base_path

        # Thread-safe structures
        self.users: Dict[str, User] = {}
        self.user_projects: Dict[str, List[str]] = {}

        self.lock = threading.Lock()

        self.init()

    # =========================================================
    # INIT (Equivalent to @PostConstruct)
    # =========================================================
    def init(self):
        self.load_users()
        self.load_user_projects()

    # =========================================================
    # LOAD USERS
    # =========================================================
    def load_users(self):
        user_file = Path(self.artefacts_base_path, "config", "user.ini")

        if not user_file.exists():
            print("user.ini not found!")
            return

        count = 0

        with user_file.open("r", encoding="utf-8") as reader:
            for line in reader:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                parts = line.split(",", 2)

                if len(parts) >= 3:
                    username = parts[0].strip()
                    password = parts[1].strip()
                    role = parts[2].strip().replace("{", "").replace("}", "")

                    with self.lock:
                        self.users[username] = User(username, password, role)

                    count += 1

        print(f"Loaded {count} users from user.ini")

    # =========================================================
    # LOAD USER PROJECTS
    # =========================================================
    def load_user_projects(self):
        file_path = Path(self.artefacts_base_path, "config", "user-project.ini")

        if not file_path.exists():
            print("user-project.ini not found!")
            return

        count = 0

        with file_path.open("r", encoding="utf-8") as reader:
            for line in reader:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                user_and_projects = line.split("~", 1)

                if len(user_and_projects) < 2:
                    continue

                username = user_and_projects[0].strip()
                project_groups = user_and_projects[1].split(",")

                projects = []

                for group in project_groups:
                    group = group.strip()

                    parts = group.split("~!~")

                    # Logic from Java:
                    # include if:
                    # 1. no type OR
                    # 2. type == "Web"
                    if len(parts) == 1 or (len(parts) > 1 and parts[1].lower() == "web"):
                        project_name = parts[0].strip()

                        if project_name:
                            projects.append(project_name)

                with self.lock:
                    self.user_projects[username] = projects

                count += 1

        print(f"Loaded project mappings for {count} users")

    # =========================================================
    # GET USER
    # =========================================================
    def get_user(self, username: str) -> User:
        return self.users.get(username)

    # =========================================================
    # GET USER PROJECTS
    # =========================================================
    def get_projects_for_user(self, username: str) -> List[str]:
        return self.user_projects.get(username, [])