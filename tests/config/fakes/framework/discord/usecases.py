class DummyRollDice:
    def __init__(self, result="ok"):
        self.result = result

    async def execute(self, expression):
        return self.result


class DummyUsecases:
    def __init__(
        self,
        narrative=None,
        roll_dice=None,
        end_session=None,
    ):
        self.narrative = narrative
        self.roll_dice = roll_dice
        self.end_session = end_session
