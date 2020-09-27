from lichessbot.command import Command
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.config import *
from lichessbot.client import *
from lichessbot.util import *

import discord


class CommandUser(Command):

	name = "user"
	help_string = "View a user's profile."
	aliases = ["profile", "player"]
	parameters = [ParamString("user id")]

	@classmethod
	async def run(self, command_call):

		user_id = command_call.args[0]

		try:
			user_public_data = client.users.get_public_data(user_id)
		except berserk.exceptions.ResponseError:
			await command_call.channel.send(f"No user exists with id `{user_id}`.")
			return

		if "closed" in user_public_data:
			await command_call.channel.send(f"Pofile of user `{user_id}` is closed.")
		else:

			embed_color = DISCORD_GREEN if user_public_data["online"] else discord.Embed.Empty

			try:
				bio = user_public_data["profile"]["bio"]
			except KeyError:
				bio = ""

			play_time = seconds_conversion(user_public_data["playTime"]["total"])

			play_time_string = ""

			for period in play_time:
				if play_time[period]:
					play_time_string += f" {play_time[period]} {period},"

			if len(play_time):
				play_time_string = f"Playtime: {play_time_string[:-1]}\n"

			player_game_gen = get_user_games(user_id)

			try:
				last_played_game_str = f"Last played game: https://lichess.org/{next(player_game_gen)['id']}\n"  
			except StopIteration:
				last_played_game_str = ""


			try:
				currently_playing_str = f"Currently playing: {user_public_data['playing']}\n"
			except KeyError:
				currently_playing_str = ""

			user_info_string = """
			{}

			{}{}
			{}
			Link: https://lichess.org/@/{}
			""".format(bio, currently_playing_str, last_played_game_str, play_time_string, user_id)

			embed = discord.Embed(title=user_public_data["username"], description=user_info_string, color=embed_color)

			await command_call.channel.send(embed=embed)