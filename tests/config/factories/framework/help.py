from discord.ext import commands


def make_help():
    class DummyHelp(commands.HelpCommand):
        async def send_bot_help(self, mapping):
            pass

    return DummyHelp()
