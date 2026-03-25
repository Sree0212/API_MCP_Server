from typing import List
from models.api_capture import ApiCapture


class ApiDataset:
    def __init__(self):
        self.captures: List[ApiCapture] = []

    def to_dict(self):
        return {
            "captures": [c.to_dict() for c in self.captures]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()

        obj.captures = [
            ApiCapture.from_dict(c)
            for c in data.get("captures", [])
        ]

        return obj