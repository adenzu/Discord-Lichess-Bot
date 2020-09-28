from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.livegames import *
from lichessbot.config import *
from lichessbot.util import *

import discord


async def create_livegame(command_call, game_id):
	game = LiveGame(game_id)
	await game.update_game()
	game.message = await command_call.channel.send(game.get_emote_representation())


class CommandWatchGame(Command):

	name = "watch-game"
	help_string = "Watch an ongoing chess game."
	aliases = []
	parameters = [ParamGameID()]

	@classmethod
	async def run(self, command_call):

		game_id = command_call.args[0]

		try:
			game_info = client.games.export(game_id)
		except berserk.exceptions.ResponseError:
			await command_call.channel.send(f"No such game is played on lichess with id `{command_call.args[0]}`")
			return

		if game_info["status"] != "started":
			await command_call.channel.send(f"Game with the id `{game_id}` is ended. Use `{COMMAND_PREFIX} gif {game_id}` instead.")
			return

		await create_livegame(command_call, game_id)


class CommandWatchUser(Command):

	name = "watch-user"
	help_string = "Watch an ongoing chess game of a player."
	aliases = []
	parameters = [ParamString("user")]

	@classmethod
	async def run(self, command_call):

		user_id = command_call.args[0]

		try:
			user_info = client.users.get_public_data(user_id)
		except berserk.exceptions.ResponseError:
			await command_call.channel.send(f"No user exists with id `{user_id}`.")
			return

		if "playing" not in user_info:
			await command_call.channel.send(f"User `{user_id}` is currently not playing a game.")
			return

		game_id = user_info["playing"].split("/")[-2]

		await create_livegame(command_call, game_id)



class CommandWatchTv(Command):

	name = "watch-tv"
	help_string = "Watch a game mode of TV channels."
	aliases = ["tv"]
	parameters = [ParamString("game mode", required=False)]

	@classmethod
	async def run(self, command_call):

		if command_call.args[0] == ParamString.null:
			game_mode = "Top Rated"
			game_id = client.games.get_tv_channels()[game_mode]["gameId"]
		else:
			game_mode = command_call.args[0].lower()

			try:
				tv_games = client.games.get_tv_channels()

				for mode in tv_games:
					if mode.lower() == game_mode:
						game_id = tv_games[mode]["gameId"]
					
				game_info = client.games.export(game_id)

			except UnboundLocalError:
				await command_call.channel.send(f"{game_mode} is not a valid game mode.")
				return


		if game_info["status"] != "started":
			await command_call.channel.send(f"Lichess TV has not selected a new {game_mode} game yet.")
			return

		await create_livegame(command_call, game_id)