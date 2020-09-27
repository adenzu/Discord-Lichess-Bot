from lichessbot.config import *

class NoCommand(Exception):
	message = f"No command was given. Type `{COMMAND_PREFIX} help`"

class NotEnoughParameters(Exception):
	message = "Not enough parameters were given."

class GameNotFound(Exception):
	message = "No game found with given id."

class CommandNotFound(Exception):
	message = "Invalid command."

class NotValidColor(Exception):
	message = "Invalid color."

class ArgOverFlow(Exception):
	message = "Too much parameters were given."