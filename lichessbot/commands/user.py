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
	parameters = [ParamUserID()]

	@classmethod
	async def run(self, command_call):

		user_id = command_call.args[0]
		user_info = client.users.get_public_data(command_call.args[0])


		if "closed" in user_info:
			await command_call.channel.send(f"Pofile of user `{user_id}` is closed.")
		else:

			embed_color = DISCORD_GREEN if user_info["online"] else discord.Embed.Empty


			try:
				bio = user_info["profile"]["bio"]
			except KeyError:
				bio = ""


			play_time = seconds_conversion(user_info["playTime"]["total"])

			play_time_string = ""

			for period in play_time:
				if play_time[period]:
					play_time_string += f" {play_time[period]} {period},"

			if sum(play_time.values()):
				play_time_string = f"\nPlaytime: {play_time_string[:-1]}\n"


			player_game_gen = get_user_games(user_id)
			try:
				last_played_game_str = f"Last played game: https://lichess.org/{next(player_game_gen)['id']}\n"  
			except StopIteration:
				last_played_game_str = ""


			try:
				currently_playing_str = f"Currently playing: {user_info['playing']}\n"
			except KeyError:
				currently_playing_str = ""


			user_info_string = """
			{}
			Member since {}

			{}{}{}
			""".format(bio, user_info["createdAt"].strftime("%m/%d/%Y"), currently_playing_str, last_played_game_str, play_time_string)


			embed = discord.Embed(title=user_info["username"], description=user_info_string, color=embed_color, url=f"https://lichess.org/@/{user_id}")

			await command_call.channel.send(embed=embed)