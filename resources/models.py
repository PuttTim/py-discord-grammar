from discord.ext import commands


class Grammar(commands.Bot):
    def __init__(self):
        # This super __init__ is to pass in parameters to the original commands.Bot from discord.py
        super().__init__(command_prefix="-")

    def set_token(self, TOKEN: int):
        self.token = TOKEN

