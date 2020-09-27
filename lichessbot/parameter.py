from lichessbot.client import client

import berserk

class Parameter():

	type_name = ""
	name = ""
	required = True

	def __init__(self, name=None, required=True):
		self.required = required
		if name:
			self.name = name

	def parse(self, command_call, arg):
		return None


class ParamString(Parameter):

	type_name = "text"
	name = "text"
	null = ""

	def parse(self, command_call, arg):
		return str(arg)


class ParamGameID(Parameter):

	type_name = "game_id"
	name = "game"
	null = None

	def parse(self, command_call, arg):

		try:
			client.games.export(arg)
			return arg
		except berserk.exceptions.ResponseError:
			return None
