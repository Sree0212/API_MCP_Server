class ApiCapture:
    def __init__(self, jsonpath: str = None, variablename: str = None):
        self.jsonPath = jsonpath
        self.variableName = variablename

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(
            jsonpath=data.get("jsonpath"),
            variablename=data.get("variablename")
        )