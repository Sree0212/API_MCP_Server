import uuid


class ApiEndpoint:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.method = None
        self.path = None
        self.summary = None
        self.sourceFile = None
        self.parameters = []
        self.headers = []
        self.requestBodySchema = None
        self.responseBodySchema = None

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        return obj