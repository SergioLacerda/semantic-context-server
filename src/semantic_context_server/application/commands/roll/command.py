class RollCommand:
    name = "roll"
    description = "Rola dados"
    usage = "/roll <expressão>"
    category = "🎲 Dados"

    def __init__(self, expression: str, user_id: int, campaign_id: str):
        self.expression = expression
        self.user_id = user_id
        self.campaign_id = campaign_id
