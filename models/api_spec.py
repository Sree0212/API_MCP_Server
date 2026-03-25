from datetime import datetime


class ApiSpec:
    def __init__(self, projectName=None, endpoints=None):
        self.projectName = projectName
        self.endpoints = endpoints or []
        self.dependencies = []
        self.discoveredAt = datetime.now()
        self.totalEndpoints = len(self.endpoints)

    def set_endpoints(self, endpoints):
        self.endpoints = endpoints or []
        self.totalEndpoints = len(self.endpoints)

    def to_dict(self):
        return {
            "projectName": self.projectName,
            "discoveredAt": self.discoveredAt.isoformat(),
            "endpoints": [e.to_dict() for e in self.endpoints],
            "totalEndpoints": self.totalEndpoints,
            "dependencies": [d.to_dict() for d in self.dependencies],
        }