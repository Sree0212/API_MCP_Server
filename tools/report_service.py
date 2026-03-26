import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


# =========================================================
# REPORT MODEL
# =========================================================
class Report:
    def __init__(self):
        self.run_id = None
        self.type = None
        self.test_script_name = None
        self.timestamp = None
        self.status = None
        self.browser = None
        self.report_url = None
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.project_name = None
        self.username = None

    def to_dict(self):
        return self.__dict__


# =========================================================
# REPORT SERVICE
# =========================================================
class ReportService:

    def __init__(self, artefacts_base_path: str):
        self.base_path = Path(artefacts_base_path)
        self.index_file = self.base_path / "reports_index.json"

        self.report_cache: List[Report] = []

        self.initialize()

    # =========================================================
    # INIT
    # =========================================================
    def initialize(self):
        self.load_index()
        self.refresh_reports()

    # =========================================================
    # LOAD INDEX
    # =========================================================
    def load_index(self):
        if self.index_file.exists():
            data = json.loads(self.index_file.read_text())
            self.report_cache = [self._dict_to_report(r) for r in data]
            print(f"Loaded {len(self.report_cache)} reports")
        else:
            print("No index file found, starting fresh")

    # =========================================================
    # REFRESH REPORTS
    # =========================================================
    def refresh_reports(self):
        last_scan = self.get_last_scan_date()
        self.scan_for_new_reports(last_scan)

    # =========================================================
    # GET REPORTS (WITH FILTERS)
    # =========================================================
    def get_reports(
        self,
        username: str,
        role: str,
        authorized_projects: List[str],
        project_filter=None,
        user_filter=None,
        type_filter=None
    ) -> List[Dict]:

        reports = [
            r for r in self.report_cache

            # 🔐 SECURITY FILTERS
            if (role.lower() == "admin" or r.username == username)
            and r.project_name in authorized_projects

            # 🎯 UI FILTERS
            and (not project_filter or project_filter == "All" or r.project_name.lower() == project_filter.lower())
            and (not user_filter or user_filter == "All" or r.username.lower() == user_filter.lower())
            and (not type_filter or type_filter == "All" or r.type.lower() == type_filter.lower())
        ]

        reports.sort(key=lambda r: r.timestamp or datetime.min, reverse=True)

        return [r.to_dict() for r in reports]

    # =========================================================
    # SCAN FILE SYSTEM
    # =========================================================
    def scan_for_new_reports(self, last_scan_date: datetime):
        user_dir = self.base_path / "User"

        if not user_dir.exists():
            return

        new_reports = []

        for file in user_dir.rglob("*"):
            if file.name not in ["summary.json", "suite_summary.json"]:
                continue

            try:
                data = json.loads(file.read_text())
                report = self._parse_report(file, data)

                if report.timestamp and report.timestamp > last_scan_date:
                    if not self._exists(report.run_id):
                        new_reports.append(report)

            except Exception as e:
                print(f"Error parsing {file}: {e}")

        if new_reports:
            print(f"Found {len(new_reports)} new reports")
            self.report_cache.extend(new_reports)
            self.persist_index()

    # =========================================================
    # PARSE REPORT
    # =========================================================
    def _parse_report(self, file: Path, data: dict) -> Report:
        r = Report()

        is_batch = file.name == "suite_summary.json"
        r.type = "batch" if is_batch else "single"

        r.run_id = data.get("runId") or data.get("suiteId")
        r.test_script_name = data.get("testScriptName")

        # Timestamp parsing
        ts = data.get("timestamp")
        if ts:
            try:
                r.timestamp = datetime.fromisoformat(ts.split(".")[0])
            except:
                r.timestamp = datetime.now()

        r.status = data.get("status")
        r.browser = data.get("browser")
        r.report_url = data.get("reportUrl")

        r.total_tests = data.get("totalTests", 0)
        r.passed = data.get("passed", 0)
        r.failed = data.get("failed", 0)
        r.errors = data.get("errors", 0)

        # 📁 PATH PARSING (IMPORTANT)
        parts = file.parts

        try:
            idx = parts.index("User")
            r.username = parts[idx + 1]
            r.project_name = parts[idx + 2]
        except:
            pass

        # fallback test name
        if not r.test_script_name:
            r.test_script_name = file.parent.parent.name

        return r

    # =========================================================
    # HELPERS
    # =========================================================
    def get_last_scan_date(self):
        if not self.report_cache:
            return datetime.fromtimestamp(0)

        return max((r.timestamp for r in self.report_cache if r.timestamp), default=datetime.fromtimestamp(0))

    def _exists(self, run_id):
        return any(r.run_id == run_id for r in self.report_cache)

    def persist_index(self):
        data = [r.to_dict() for r in self.report_cache]
        self.index_file.write_text(json.dumps(data, indent=2))
        print("Saved report index")

    def _dict_to_report(self, data):
        r = Report()
        r.__dict__.update(data)

        if isinstance(r.timestamp, str):
            try:
                r.timestamp = datetime.fromisoformat(r.timestamp)
            except:
                r.timestamp = None

        return r