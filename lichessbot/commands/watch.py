from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.livegames import *
from lichessbot.config import *
from lichessbot.util import *

import discord


class CommandWatchGame(Command):

	name = "watch-game"
	help_string = "Watch an ongoing chess game."
	aliases = []
	parameters = [ParamGameID()]
	enabled = False

	@classmethod
	async def run(cls, command_call):

		game_id = command_call.args[0]

		try:
			game_info = client.games.export(game_id)
		except berserk.exceptions.ResponseError:
			await command_call.channel.send(f"No such game is played on lichess with id `{command_call.args[0]}`")
			return

		if game_info["status"] != "started":
			await command_call.channel.send(f"Game with the id `{game_id}` is ended. Use `{COMMAND_PREFIX} gif {game_id}` instead.")
			return

		if not await create_livegame(command_call, game_id, game_info):
			await command_call.channel.send(f"Game with id `{game_id}` is already being watched in this channel!")


class CommandWatchUser(Command):

	name = "watch-user"
	help_string = "Watch an ongoing chess game of a player."
	aliases = []
	parameters = [ParamUserID()]
	enabled = False

	@classmethod
	async def run(cls, command_call):

		user_info = client.users.get_public_data(command_call.args[0])

		if "playing" not in user_info:
			await command_call.channel.send(f"User `{command_call.args[0]}` is currently not playing a game.")
			return

		game_id = user_info["playing"].split("/")[-2]

		if not await create_livegame(command_call, game_id, client.games.export(game_id)):
			await command_call.channel.send(f"User `{command_call.args[0]}` is already being watched in this channel!")


class CommandWatchTv(Command):

	name = "watch-tv"
	help_string = "Watch a game mode of TV channels."
	aliases = ["tv"]
	parameters = [ParamGameMode(required=False)]
	enabled = False

	@classmethod
	async def run(cls, command_call):

		game_mode = command_call.args[0]
		game_id = client.games.get_tv_channels()[game_mode]["gameId"]
		game_info = client.games.export(game_id)

		try:
			game_info = client.games.export(game_id)

		except UnboundLocalError:
			await command_call.channel.send(f"{game_mode} is not a valid game mode.")
			return

		if game_info["status"] != "started":
			await command_call.channel.send(f"Lichess TV has not selected a new {game_mode} game yet.")
			return

		if not await create_livegame(command_call, game_id, game_info):
			await command_call.channel.send(f"Game with game mode `{game_mode}` is already being watched in this channel!")


class CommandWatch(Command):

	name = "watch"
	help_string = "Watch a game or a user or a game mode of TV channels."
	aliases = []
	parameters = [ParamUnion(ParamGameID(), ParamGameMode(), ParamUserID(), required=False, default_class=ParamGameMode)]

	@classmethod
	async def run(cls, command_call):

		parsed_class = cls.parameters[0].get_parsed_class()

		if parsed_class == ParamGameID:
			await CommandWatchGame.call(command_call)
		elif parsed_class == ParamGameMode:
			await CommandWatchTv.call(command_call)
		elif parsed_class == ParamUserID:
			await CommandWatchUser.call(command_call)