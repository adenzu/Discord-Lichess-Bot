from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.util import *

import berserk

class CommandGif(Command):

	name = "gif"
	help_string = "View gif of a chess game."
	aliases = []
	parameters = [ParamGameID(), ParamColor(required=False)]

	@classmethod
	async def run(cls, command_call):

		try:
			game = client.games.export(command_call.args[0])
			await command_call.channel.send(f"https://lichess1.org/game/export/gif{command_call.args[1]}/{command_call.args[0]}.gif")
		except berserk.exceptions.ResponseError:
			await command_call.channel.send(f"No such game is played on lichess with id `{command_call.args[0]}`")


