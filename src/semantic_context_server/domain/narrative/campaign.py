class Campaign:
    def __init__(self, campaign_id: str):
        self.id = campaign_id

    def build_context(self, events: list[str], max_chars: int) -> str:
        size = 0
        selected = []

        for e in reversed(events):
            size += len(e)

            if size > max_chars:
                break

            selected.append(e)

        return "\n".join(reversed(selected))
