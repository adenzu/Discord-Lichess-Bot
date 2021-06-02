from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.util import *


class CommandHelp(Command):

	name = "help"
	help_string = "View available commands."
	aliases = ["commands"]
	parameters = [ParamString("command", required=False)]

	@classmethod
	async def run(cls, command_call):

		response = ""

		for command in Command.__subclasses__():

			if command.enabled:

				response += f"`{command.usage_string()}`\n{command.help_string}\n\n"

				if command_call.args[0] == command.name or command_call.args[0] in command.aliases:
					await command_call.channel.send(f"`{command.usage_string()}`\n{command.help_string}")
					return

		await command_call.author.send(f"`[param]` parameters are required for the command, `<param>` parameters are not mandatory.\n\n{response}")
