from lichessbot.exceptions import *
from lichessbot.util import *

class Command():

	name = ""
	help_string = ""
	aliases = []
	parameters = []
	enabled = True

	@classmethod
	async def call(self, command_call):

		if len(command_call.raw_args) > len(self.parameters):
			await command_call.channel.send(f"Too much input!\nUsage: `{self.usage_string()}`")

		else:

			for i in range(len(self.parameters)):

				curr_param = self.parameters[i]
				command_call.args.append(curr_param.default)

				try:
					parsed_arg = curr_param.parse(command_call, command_call.raw_args[i])

					if parsed_arg == None:
						await command_call.channel.send(f"Invalid input for: `{curr_param.name}` of type `{curr_param.type_name}`!\nUsage: `{self.usage_string()}`")
						return

					command_call.args[i] = parsed_arg

				except IndexError:

					if curr_param.required:
						await command_call.channel.send(f"You must specify: `{curr_param.name}` of type `{curr_param.type_name}`!\nUsage: `{self.usage_string()}`")
						return

			await self.run(command_call)

	@classmethod
	async def run(self, command_call):
		pass

	@classmethod
	def usage_string(self):

		usg_str = f"{COMMAND_PREFIX} {self.name}"

		for param in self.parameters:

			if param.required:
				usg_str += f" [{param.get_name()}]"
			else:
				usg_str += f" <{param.get_name()}>"

		return usg_str