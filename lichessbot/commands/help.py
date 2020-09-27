from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.util import *

class CommandHelp(Command):

	name = "help"
	help_string = "View available commands."
	aliases = ["commands", ""]
	parameters = []

	@classmethod
	async def run(self, command_call):

		response = ""

		for c in Command.__subclasses__():
			response += f"`{c.usage_string()}`\n{c.help_string}\n\n"

		await command_call.author.send(response)