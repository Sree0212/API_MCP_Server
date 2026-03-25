class ApiHealAction:
    def __init__(
        self,
        actionType: str = None,
        target: str = None,
        key: str = None,
        value=None,
        reason: str = None,
    ):
        self.actionType = actionType
        self.target = target
        self.key = key
        self.value = value
        self.reason = reason

    @staticmethod
    def from_dict(data: dict):
        return ApiHealAction(
            actionType=data.get("actionType"),
            target=data.get("target"),
            key=data.get("key"),
            value=data.get("value"),
            reason=data.get("reason"),
        )

    def to_dict(self):
        return {
            "actionType": self.actionType,
            "target": self.target,
            "key": self.key,
            "value": self.value,
            "reason": self.reason,
        }