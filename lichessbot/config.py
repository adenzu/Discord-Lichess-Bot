from lichessbot.command import Command
from lichessbot.client import client


from dotenv import load_dotenv
load_dotenv()

import os
import discord



COMMAND_LIST = Command.__subclasses__()


BOT_TOKEN = os.getenv("BOT_TOKEN")


COMMAND_PREFIX = "!lc"


DISCORD_GREEN = discord.Color.from_rgb(120, 177, 89)


LIVE_GAME_REFRESH_RATE = 0.2


EMOTE_PIECE_SYMBOLS = {
    "R0": "<:wr0:757566867521929257>", "r0" : "<:br0:757566865227907083>",
    "N0": "<:wn0:757566866171625534>", "n0" : "<:bn0:757566863998844959>",
    "B0": "<:wb0:757566865533960232>", "b0" : "<:bb0:757566862942011392>",
    "Q0": "<:wq0:757566866913886270>", "q0" : "<:bq0:757566864502030368>",
    "K0": "<:wk0:757566865940938842>", "k0" : "<:bk0:757566863394865162>",
    "P0": "<:wp0:757566866721079397>", "p0" : "<:bp0:757566864359686154>",
    "R1": "<:wr1:757566867769393253>", "r1" : "<:br1:757566865253072948>",
    "N1": "<:wn1:757566866242928671>", "n1" : "<:bn1:757566864158228490>",
    "B1": "<:wb1:757566866779668580>", "b1" : "<:bb1:757566862820114433>",
    "Q1": "<:wq1:757566867295567943>", "q1" : "<:bq1:757566865055940699>",
    "K1": "<:wk1:757566866482004039>", "k1" : "<:bk1:757566863755575366>",
    "P1": "<:wp1:757566866964349028>", "p1" : "<:bp1:757566864573595658>",
    ".1": "<:blank1:757566863608774679>", ".0" : "<:blank0:757566863684272228>"
}


GAME_MODES = list(client.games.get_tv_channels().keys())