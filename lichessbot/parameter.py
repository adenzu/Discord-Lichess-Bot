from lichessbot.client import client
from lichessbot.config import *

import berserk


class Parameter():

	type_name = ""
	name = ""
	required = True
	null = None

	def __init__(self, name=None, required=True, null=None):
		self.required = required
		self.null = null
		if name:
			self.name = name

	def parse(self, command_call, arg):
		return None


class ParamString(Parameter):

	type_name = "text"
	name = "text"
	null = ""

	def parse(self, command_call, arg):
		return str(arg) if self.required else self.null


class ParamGameID(Parameter):

	type_name = "game_id"
	name = "game"
	null = ""

	def parse(self, command_call, arg):

		try:
			client.games.export(arg)
			return arg
		except berserk.exceptions.ResponseError:
			return None if self.required else self.null


class ParamUserID(Parameter):

	type_name = "user_id"
	name = "user"
	null = ""

	def parse(self, command_call, arg):

		if len(client.users.get_by_id(arg)):
			return args
		return None if self.required else self.null


class ParamGameMode(Parameter):

	type_name = "game_mode"
	name = "mode"
	null = ""

	def parse(self, command_call, arg):

		for mode in GAME_MODES:
			if arg.lower() == mode.lower():
				return mode
		return None if self.required else self.null


class ParamCommand(Parameter):

	type_name = "bot_command"
	name = "command"
	null = ""

	def parse(self, command_call, arg):

		if arg in COMMAND_LIST:
			return arg
		return None if self.required else self.null


class ParamColor(Parameter):

	type_name = "color"
	name = "color"
	null = ""

	def parse(self, command_call, arg):

		for color in ("white", "black"):
			if arg.lower() == color:
				return color
		return None if self.required else self.null