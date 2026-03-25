from typing import List
from models.api_endpoint import ApiEndpoint


class ApiGroup:
    def __init__(self, name: str):
        self.name = name
        self.endpoints: List[ApiEndpoint] = []

    def to_dict(self):
        return {
            "name": self.name,
            "endpoints": [e.to_dict() for e in self.endpoints]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data.get("name"))
        obj.endpoints = [ApiEndpoint.from_dict(e) for e in data.get("endpoints", [])]
        return obj