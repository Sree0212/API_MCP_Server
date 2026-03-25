from typing import List, Dict
from models.api_group import ApiGroup
from models.api_dependency import ApiDependency


class ApiCollection:
    def __init__(self, id: str):
        self.id = id
        self.groups: List[ApiGroup] = []
        self.dependencies: List[ApiDependency] = []
        self.variables: Dict[str, str] = {}

    def to_dict(self):
        return {
            "id": self.id,
            "groups": [g.to_dict() for g in self.groups],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "variables": self.variables
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("id"))

        obj.groups = [
            ApiGroup.from_dict(g) for g in data.get("groups", [])
        ]

        obj.dependencies = [
            ApiDependency.from_dict(d) for d in data.get("dependencies", [])
        ]

        obj.variables = data.get("variables", {})

        return obj