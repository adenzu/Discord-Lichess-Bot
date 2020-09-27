from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.config import *
from lichessbot.util import *

import discord

class CommandRatings(Command):

	name = "ratings"
	help_string = "View a user's ratings."
	aliases = ["rating"]
	parameters = [ParamString("user id")]

	@classmethod
	async def run(self, command_call):

		user_id = command_call.args[0]

		try:
			user_info = client.users.get_by_id(user_id)
		except UnicodeEncodeError:
			await command_call.channel.send(f"No user exists with id `{user_id}`.")
			return

		if not len(user_info):
			await command_call.channel.send(f"No user exists with id `{user_id}`.")
		elif "disabled" in user_info[0]:
			await command_call.channel.send(f"Pofile of user `{user_id}` is closed.")
		else:

			user_info = user_info[0]

			embed_color = DISCORD_GREEN if user_info["online"] else discord.Embed.Empty

			embed = discord.Embed(title=f"{user_info['username']} ratings".title(), color=embed_color)

			for mode in user_info["perfs"]:
				if user_info["perfs"][mode]["games"]:
					embed.add_field(name=mode.title(), value=f"**{user_info['perfs'][mode]['rating']}** ({user_info['perfs'][mode]['games']} {'puzzles' if mode == 'puzzle' else 'games'})", inline=True)

			await command_call.channel.send(embed=embed)

