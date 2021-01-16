from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.livegames import *
from lichessbot.config import *
from lichessbot.util import *

import discord

class CommandWatchGame(Command):

	name = "stop"
	help_string = "Stop streaming an ongoing chess game."
	aliases = ["abort"]
	parameters = [ParamInteger(required=False)]
	enabled = True

	@classmethod
	async def run(cls, command_call):

		game_index = command_call.args[0]

		chosen_game = None

		for game in ongoing_games[::-1]:
			
			if game.author == command_call.author and game.board_message.channel == command_call.channel:
				game_index -= 1
				
				if not game_index:
					chosen_game = game
					break


		if chosen_game:
			await chosen_game.board_message.edit(content=f"{chosen_game.board_message.content}\n\n{command_call.author.name} stopped stream.")
			ongoing_games.remove(chosen_game)
		else:
			await command_call.channel.send(f"You have started watching only `{command_call.args[0]-game_index}` games that are still being streamed!")