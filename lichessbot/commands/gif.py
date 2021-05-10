from lichessbot.command import Command
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.client import *
from lichessbot.util import *

import berserk

class CommandGif(Command):

	name = "gif"
	help_string = "View gif of a chess game."
	aliases = []
	parameters = [ParamUnion(ParamGameID(), ParamUserID()), ParamColor(required=False)]

	@classmethod
	async def run(cls, command_call):

		parsed_class = cls.parameters[0].get_parsed_class()
		game_id = command_call.args[0]
		
		if parsed_class == ParamUserID:
			
			user_id = command_call.args[0]
			user_info = client.users.get_public_data(user_id)

			if "playing" in user_info:
				await command_call.channel.send(f"User `{user_id}` is currently playing a game. Use `!lc watch {user_id}` instead.")
				return

			player_game_gen = get_user_games(user_id)
			game_id = next(player_game_gen)["id"]
			
		try:
			game = client.games.export(game_id)
			await command_call.channel.send(f"https://lichess1.org/game/export/gif{command_call.args[1]}/{game_id}.gif")
		except berserk.exceptions.ResponseError:
			await command_call.channel.send(f"No such game is played on lichess with id `{game_id}`")

