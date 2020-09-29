from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.config import *
from lichessbot.util import *

import discord

class CommandStats(Command):

	name = "stats"
	help_string = "View a user's game stats."
	aliases = ["statistics"]
	parameters = [ParamUserID()]

	@classmethod
	async def run(self, command_call):

		user_info = client.users.get_public_data(command_call.args[0])

		if "closed" in user_info:
			await command_call.channel.send(f"Pofile of user `{user_id}` is closed.")
		else:

			embed_color = DISCORD_GREEN if user_info["online"] else discord.Embed.Empty

			embed = discord.Embed(title=f"{user_info['username']} stats".title(), color=embed_color)

			is_perf = False

			for mode in user_info["perfs"]:
				if user_info["perfs"][mode]["games"]:
					is_perf = True
					embed.add_field(name=mode.title(), value=f"**{user_info['perfs'][mode]['rating']}** ({user_info['perfs'][mode]['games']} {'puzzles' if mode == 'puzzle' else 'games'})", inline=True)

			if is_perf:
				embed.add_field(name="\u2800",value= "\u2800",inline=False)

			for status in user_info["count"]:
				if not status.endswith("H"):
					embed.add_field(name=status.title(), value=f"{user_info['count'][status]}")
				elif status == "winH":
					break

			await command_call.channel.send(embed=embed)

