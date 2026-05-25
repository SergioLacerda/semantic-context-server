class SessionCommand:
    name = "endsession"
    description = "Finaliza sessão"
    usage = "/endsession"
    category = "🛑 Sessão"

    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
