import json
import uuid
from pathlib import Path
from typing import List, Dict


class ReusableModuleService:

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    # =========================================================
    # PATH HELPERS
    # =========================================================
    def _module_dir(self, project, module):
        return self.base_path / "Main" / project / "reusable_modules" / module

    def _modules_root(self, project):
        return self.base_path / "Main" / project / "reusable_modules"

    # =========================================================
    # GET ALL MODULES
    # =========================================================
    def get_all_modules(self, project) -> List[Dict]:
        root = self._modules_root(project)
        if not root.exists():
            return []

        modules = []
        for d in root.iterdir():
            meta = d / "module.json"
            if meta.exists():
                modules.append(json.loads(meta.read_text()))

        return modules

    # =========================================================
    # CREATE MODULE
    # =========================================================
    def create_module(
        self,
        project,
        module_name,
        description,
        initial_code,
        initial_repo=None
    ):
        module_dir = self._module_dir(project, module_name)

        if module_dir.exists():
            raise Exception("Module already exists")

        # Create structure
        (module_dir / "datasets").mkdir(parents=True)

        module = {
            "name": module_name,
            "description": description,
            "versions": ["default"],
            "currentVersion": "default",
            "versionMetadata": {
                "default": {
                    "dataKeys": [],
                    "locatorKeys": []
                }
            }
        }

        self._save_meta(project, module_name, module)

        # Create script
        script = self._generate_script(module_name, "default", initial_code)
        (module_dir / "script.py").write_text(script)

        # Object repo
        repo = initial_repo or {}
        (module_dir / "object_repository.json").write_text(json.dumps(repo, indent=2))

        # Dataset
        dataset = [{
            "id": str(uuid.uuid4()),
            "name": "default",
            "values": {}
        }]

        self.save_datasets(project, module_name, "default", dataset)

        return module

    # =========================================================
    # DATASETS
    # =========================================================
    def get_datasets(self, project, module, version):
        file = self._module_dir(project, module) / "datasets" / f"{version}.json"
        if not file.exists():
            return []
        return json.loads(file.read_text())

    def save_datasets(self, project, module, version, data):
        file = self._module_dir(project, module) / "datasets" / f"{version}.json"
        file.write_text(json.dumps(data, indent=2))

    # =========================================================
    # VERSION MANAGEMENT
    # =========================================================
    def create_version(self, project, module, base_version, new_version):
        meta = self._load_meta(project, module)

        if new_version in meta["versions"]:
            raise Exception("Version exists")

        script_file = self._module_dir(project, module) / "script.py"
        content = script_file.read_text()

        base_func = self._func_name(module, base_version)
        new_func = self._func_name(module, new_version)

        body = self._extract_body(content, base_func)

        new_content = content + "\n" + self._wrap_function(new_func, body)
        script_file.write_text(new_content)

        meta["versions"].append(new_version)
        meta["currentVersion"] = new_version

        self._save_meta(project, module, meta)

        # Copy dataset
        base_ds = self.get_datasets(project, module, base_version)
        self.save_datasets(project, module, new_version, base_ds)

    # =========================================================
    # OBJECT REPO
    # =========================================================
    def get_repo(self, project, module):
        file = self._module_dir(project, module) / "object_repository.json"
        if not file.exists():
            return {}
        return json.loads(file.read_text())

    def save_repo(self, project, module, repo):
        file = self._module_dir(project, module) / "object_repository.json"
        file.write_text(json.dumps(repo, indent=2))

    # =========================================================
    # HELPERS
    # =========================================================
    def _save_meta(self, project, module, data):
        file = self._module_dir(project, module) / "module.json"
        file.write_text(json.dumps(data, indent=2))

    def _load_meta(self, project, module):
        file = self._module_dir(project, module) / "module.json"
        return json.loads(file.read_text())

    def _func_name(self, module, version):
        return f"{module}_{version.replace('-', '_')}"

    def _generate_script(self, module, version, body):
        func = self._func_name(module, version)
        return f"""
def {func}(context):
{self._indent(body)}
"""

    def _wrap_function(self, name, body):
        return f"\ndef {name}(context):\n{self._indent(body)}\n"

    def _indent(self, text):
        return "\n".join("    " + line for line in text.split("\n"))

    def _extract_body(self, content, func):
        import re
        m = re.search(rf"def {func}\(context\):(.*?)(?=\ndef|\Z)", content, re.S)
        return m.group(1) if m else ""