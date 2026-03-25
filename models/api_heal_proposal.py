from models.api_heal_action import ApiHealAction


class ApiHealProposal:
    def __init__(self, diagnosis=None, actions=None):
        self.diagnosis = diagnosis
        self.actions = actions or []
        self.applied = False
        self.collectionBackup = None
        self.datasetBackup = None

    @staticmethod
    def from_dict(data: dict):
        actions = [
            ApiHealAction.from_dict(a)
            for a in data.get("actions", [])
        ]

        obj = ApiHealProposal(
            diagnosis=data.get("diagnosis"),
            actions=actions,
        )

        return obj

    def to_dict(self):
        return {
            "diagnosis": self.diagnosis,
            "actions": [a.to_dict() for a in self.actions],
            "applied": self.applied,
            "collectionBackup": self.collectionBackup,
            "datasetBackup": self.datasetBackup,
        }