class DummyCampaignState:
    def __init__(self, campaign_id=None, use_default=False):
        self._data = {}
        self._use_default = use_default

        if campaign_id is not None:
            self._data["default"] = campaign_id

    def get(self, channel_id):
        if channel_id in self._data:
            return self._data[channel_id]

        if self._use_default:
            return self._data.get("default")

        return None

    def set(self, channel_id, campaign_id):
        self._data[channel_id] = campaign_id

    def clear(self, channel_id):
        self._data.pop(channel_id, None)


class FakeCampaignState:
    def __init__(self, campaign_id="test_campaign"):
        self.current_campaign = campaign_id


class DummyCreateCampaign:
    async def execute(self, name: str):
        return True


class DummyListCampaigns:
    async def execute(self):
        return ["aventura"]


class DummyDeleteCampaign:
    async def execute(self, name: str):
        return True
