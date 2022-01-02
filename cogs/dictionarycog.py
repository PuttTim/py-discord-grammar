import discord
from discord.commands.commands import option
from discord.ext import commands
from discord.commands import slash_command, Option, OptionChoice


import requests
import io
import aiohttp

from resources import models, helpers
from api.collegiate import collegiate_request

guilds = [
    734360871521746975,
    907846995127980053,
    832654835127156806,
    881078342122606684,
]


def definition_embed(response: dict):
    embed = helpers.create_embed(response["word"])

    embed.add_field(inline=False, name="Label", value=response["label"])
    embed.add_field(inline=False, name="Definition", value=response["definition"])
    embed.add_field(inline=False, name="Pronunciation", value=response["text_pr"])

    return embed


async def get_audiofile(audio_url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(audio_url) as resp:
            if resp.status != 200:
                return "Could not download audio file..."
            data = io.BytesIO(await resp.read())
            return data


class AudioButton(discord.ui.View):
    def __init__(self, word, audio_url, hide):
        super().__init__()
        self.value = None
        self.word = word
        self.audio_url = audio_url
        self.hide = hide

    @discord.ui.button(label="🔊 Audio", style=discord.ButtonStyle.secondary)
    async def upload_audio(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        data = await get_audiofile(self.audio_url)

        if self.hide == "None" or self.hide == "True":
            await interaction.response.send_message(
                file=discord.File(data, f"{self.word}.mp3"), ephemeral=True
            )
        elif self.hide == "False":
            await interaction.response.send_message(
                file=discord.File(data, f"{self.word}.mp3"), ephemeral=False
            )

        self.value = True

        button.disabled = True

        await interaction.message.edit(view=self)

        # await self.ctx.edit(view=None)
        self.stop()


class SuggestionSelect(discord.ui.Select):
    def __init__(self, ctx: discord.ApplicationContext, suggestions: list, hide: str):
        self.ctx = ctx
        self.hide = hide

        options = []
        for suggestion in suggestions:
            options.append(discord.SelectOption(label=suggestion))

        super().__init__(
            placeholder="Did you mean..",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # print(type(self._selected_values))
        # print(self._selected_values)
        word = self._selected_values[0]
        response = collegiate_request(word)
        embed = definition_embed(response)

        if self.hide == "None" or self.hide == "True":
            await interaction.response.send_message(
                embed=embed,
                view=AudioButton(
                    word=word, audio_url=response["audio_url"], hide=self.hide
                ),
                ephemeral=True,
            )
        elif self.hide == "False":
            await interaction.response.send_message(
                embed=embed,
                view=AudioButton(
                    word=word, audio_url=response["audio_url"], hide=self.hide
                ),
                ephemeral=False,
            )


class SuggestionView(discord.ui.View):
    def __init__(self, ctx: discord.ApplicationContext, suggestions: list, hide: str):
        self.ctx = ctx
        self.hide = hide
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(SuggestionSelect(ctx, suggestions, hide))


class Dictionary(commands.Cog):
    def __init__(self, bot: models.Grammar):
        self.bot = bot

    def get_bot(self):
        return self.bot

    @slash_command(
        name="definition",
        description="Search for a definition of a word",
        guild_ids=guilds,
    )
    @option(
        "word",
        discord.enums.SlashCommandOptionType.string,
        description="Search your word in the Collegiate Dictionary",
        required=True,
    )
    @option(
        "hide",
        discord.enums.SlashCommandOptionType.string,
        description="Hides the reply to this command",
        required=True,
        choices=[
            OptionChoice(name="True", value="True"),
            OptionChoice(name="False", value="False"),
        ],
    )
    async def definition(self, ctx: discord.ApplicationContext, word: str, hide: str):
        word = word.lower()

        if hide == None or hide == "True":
            await ctx.defer(ephemeral=True)
        else:
            await ctx.defer(ephemeral=False)

        response = collegiate_request(word)

        if response["type"] != "suggestion":
            embed = definition_embed(response)
            await ctx.followup.send(
                embed=embed,
                view=AudioButton(word=word, audio_url=response["audio_url"], hide=hide),
            )
        elif response["error"] != None:
            embed = helpers.create_embed("Error!").add_field(
                name="HTTP Error", value=response["error"]
            )
            await ctx.followup.send(embed=embed)
        elif response["type"] == "suggestion":
            embed = helpers.create_embed(f"{word} not found..").add_field(
                name="Did you mean..",
                value="*Try selecting one of the suggested words!*",
            )
            await ctx.followup.send(
                embed=embed,
                view=SuggestionView(
                    ctx=ctx, suggestions=response["suggestion"], hide=hide
                ),
            )


def setup(bot):
    bot.add_cog(Dictionary(bot))
    print("definition cog loaded")
