import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

from resources import helpers, models

load_dotenv(".env")

# Accessing environment variables.
TOKEN = os.getenv("TOKEN")

bot = models.Grammar()

guilds = [734360871521746975, 907846995127980053]
bot.set_token(TOKEN)
cogs_list = ["dictionarycog"]


@bot.event
async def on_ready():
    print("Main bot zooooooom")
    print("Loading guilds..")
    for guild in bot.guilds:
        print(f'Guild "{guild.name}" loaded')

    await bot.change_presence(
        activity=discord.Activity(
            name=f"Built at: {helpers.get_current_time()}",
            type=discord.ActivityType.playing,
        )
    )


@bot.command(name="embed")
async def embed(ctx):
    await ctx.reply(embed=helpers.create_embed("Word"))


if __name__ == "__main__":
    for extension in cogs_list:
        try:
            bot.load_extension("cogs." + extension)
        except Exception as e:
            print(f"{e}")

    bot.run(bot.token)
