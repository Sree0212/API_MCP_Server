class ApiDependency:
    def __init__(self):
        self.sourceId = None
        self.targetId = None
        self.parameterName = None
        self.relationshipType = None

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        return obj