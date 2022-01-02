from datetime import datetime
from discord import Embed


def get_current_time():
    return f'{datetime.now().strftime("%X")}'


def create_embed(title):
    return Embed(title=title).set_footer(
        text="Powered by Merriam-Webster | Grammar Bot v0.1.0",
        icon_url="https://dictionaryapi.com/images/info/branding-guidelines/MWLogo_DarkBG_120x120_2x.png",
    )
