from lichessbot.command import Command
from lichessbot.client import client
from lichessbot.config import *
import lichessbot.commands

import berserk

COMMAND_LIST = Command.__subclasses__()

class Parameter():

	type_name = ""
	name = ""
	required = True
	default = None

	def __init__(self, name=None, required=True, default=None):
		self.required = required
		
		if default:
			self.default = default
		if name:
			self.name = name

	def parse(self, command_call, arg):
		return None

	def get_name(self):
		return self.name

	def get_type_name(self):
		return self.type_name


class ParamString(Parameter):

	type_name = "text"
	name = "text"
	default = None

	def parse(self, command_call, arg):
		return str(arg)


class ParamGameID(Parameter):

	type_name = "game_id"
	name = "game"
	default = None

	def parse(self, command_call, arg):

		try:
			client.games.export(arg)
			return arg
		except berserk.exceptions.ResponseError:
			return None 


class ParamUserID(Parameter):

	type_name = "user_id"
	name = "user"
	default = None

	def parse(self, command_call, arg):

		try:
			if len(client.users.get_by_id(arg)):
				return arg
		except:
			return None
		return None 


class ParamGameMode(Parameter):

	type_name = "game_mode"
	name = "mode"
	default = "Top Rated"

	def parse(self, command_call, arg):

		valid_arg = arg.lower().replace("_", " ")

		for mode in GAME_MODES:
			if valid_arg == mode.lower():
				return mode
				
		return None 


class ParamColor(Parameter):

	type_name = "color"
	name = "color"
	default = ""

	def parse(self, command_call, arg):

		if arg.lower() in ("white", "black"):
			return "/" + arg.lower()
		return None 


class ParamInteger(Parameter):

	type_name = "number"
	name = "number"
	default = 1

	def parse(self, command_call, arg):

		try:
			return int(arg)
		except ValueError:
			return None


class ParamTournamentID(Parameter):
	
	type_name = "tournament_id"
	name = "tournament"
	default = None

	def parse(self, command_call, arg):

		try:
			client.tournaments.stream_results(arg)
			return arg
		except berserk.exceptions.ResponseError:
			return None 

class ParamUnion(Parameter):

	params = []
	type_names = []
	names = []
	default = None

	default_param_class = None
	parsed_class = None

	def __init__(self, *params, name=None, required=True, default_class=None):

		self.params = params
		self.type_names = [param.get_type_name() for param in params]
		self.names = [param.get_name() for param in params]

		self.required = required
		
		if default_class:
			self.default_param_class = default_class
			self.default = default_class.default
			self.parsed_class = default_class
		if name:
			self.name = name

	def parse(self, command_call, arg):

		for param in self.params:
			curr_parse = param.parse(command_call, arg)
			if curr_parse:
				self.parsed_class = param.__class__
				return curr_parse
				
		return None 

	# Credit for the bugfix goes to godofmilker
	def get_parsed_class(self):

		parsed_class = self.parsed_class
		self.parsed_class = self.default_param_class

		return parsed_class

	def get_type_name(self):
		return "|".join(self.type_names)

	def get_name(self):
		return "|".join(self.names)