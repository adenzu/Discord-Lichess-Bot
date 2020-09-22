import cairosvg
from PIL import Image
from io import BytesIO
import lichess.api
import chess.svg
import chess
import discord
import asyncio


# Get bot token.
token = ""
with open("token.txt", "r") as token_file:
	token = token_file.read()

# Start client.
client = discord.Client()

# Enum variables for error handlings.
ACCOUNT_CLOSED 		= 0
GAME_NOT_FOUND 		= 1
COMMAND_NOT_FOUND 	= 2
ACCOUNT_NOT_FOUND 	= 3
PLAYED_ZERO_GAMES 	= 4
GAME_NOT_LIVE 		= 5
GAME_LIVE 			= 6
NO_NEW_MOVE 		= 7

# Some of Discord's emote colours.
DISCORD_GREEN = discord.Colour.from_rgb(120, 177, 59)
DISCORD_BLACK = discord.Colour.from_rgb(49, 55, 61)

# Command prefix for bot to understand commands.
COMMAND_PREFIX = "!lc"

# You can watch chess games on lichess real time. This variable is the duration between move checks for live games.
LIVE_GAMES_REFRESH_RATE = 0.05

# Dictionary for explaining how to use existing commands.
command_usages = {
	"help" : f"{COMMAND_PREFIX} help <command>",
	"user" : f"{COMMAND_PREFIX} user [user name]",
	"gif"  : f"{COMMAND_PREFIX} gif [game id]",
	"watch": f"{COMMAND_PREFIX} watch [game id]",
	"tv"   : f"{COMMAND_PREFIX} tv [game type]"
}

# Dictionary for explaining how existing commands work.
command_explanations = {
	"help" : "Explains given command. If no command is given explains how command `help` works and shows other commands. <...> indicates the parameter is optional, [...] means it's obligatory.",
	"user" : "Gives information about given user.",
	"gif"  : "Sends gif of the given game.",
	"watch": "Shows given game's current situation.",
	"tv"   : "Shows current streaming chess game with given game type.",
}

# This dictionary is for converting pychess board ASCII graphic to discort emote-image-thingy.
# 
# PROBLEM: Since one board consists of 64 squares, 64 emotes are used for representing the board,
# thus emotes in final message gets shrinked.
EMOTE_PIECE_SYMBOLS = {
    "R0": "<:wr0:757566867521929257>", "r0" : "<:br0:757566865227907083>",
    "N0": "<:wn0:757566866171625534>", "n0" : "<:bn0:757566863998844959>",
    "B0": "<:wb0:757566865533960232>", "b0" : "<:bb0:757566862942011392>",
    "Q0": "<:wq0:757566866913886270>", "q0" : "<:bq0:757566864502030368>",
    "K0": "<:wk0:757566865940938842>", "k0" : "<:bk0:757566863394865162>",
    "P0": "<:wp0:757566866721079397>", "p0" : "<:bp0:757566864359686154>",
    "R1": "<:wr1:757566867769393253>", "r1" : "<:br1:757566865253072948>",
    "N1": "<:wn1:757566866242928671>", "n1" : "<:bn1:757566864158228490>",
    "B1": "<:wb1:757566866779668580>", "b1" : "<:bb1:757566862820114433>",
    "Q1": "<:wq1:757566867295567943>", "q1" : "<:bq1:757566865055940699>",
    "K1": "<:wk1:757566866482004039>", "k1" : "<:bk1:757566863755575366>",
    "P1": "<:wp1:757566866964349028>", "p1" : "<:bp1:757566864573595658>",
      1 : "<:blank1:757566863608774679>", 0 : "<:blank0:757566863684272228>"
}

# This list contains live games that are watched through discord.
live_games = []

# Class for the live games so they can be managed more easily.
# 
# PROBLEM: 	The emote representation of board is created from scratch whenever there's 
# 			a new move to edit the message, not efficient.
# FIX:		Emote representation of the board can be stored in a 2D array, and altered
# 			just slightly for the new moves.
class LiveGame:

	# @param {str} game_id An id of a chess game that is played on lichess.
	def __init__(self, game_id):

		self.game_id  = game_id 		# Stores its game id, since lichess.api returns not an object for a game
										# but a dictionary for current status for it, this will be needed.  
		self.board    = chess.Board() 	# Initializes new chess board for the game. 
		self.moves    = ""				# Contains all the moves that is played til now.
		self.message  = None 			# Whenever a new move is played, the message that contains game's 
										# representation (consisting of emotes) has to be updated, thus
										# has to be stored to be edited later.
		self.new_move = False

		self.update_game()	# To create new needed variables and update existing ones.


	# Equality result is dependant on the game's id. Not the object itself.
	# @param  {_}		other 	The other value in the equality operation.
	# @return {boolean}			The result of logical equality operation.
	def __eq__(self, other):

		if type(other) == LiveGame:				 # Specify the probability of two LiveGame object equality operation.
												 # Otherwise unlimited recursion is sure to appear.
			return self.game_id == other.game_id
		return self.game_id == other # In this case 'other' may be a string consisting of a game id.


	# Updates already existing variables, and creates some when it's ran for the first time.
	def update_game(self):
		game = get_game_with_id(self.game_id)	# Gets game's status dict with function get_game_with_id. 

		if game == GAME_NOT_FOUND:			# If instead of a dictionary, warning GAME_NOT_FOUND is returned.
			self.status =  GAME_NOT_FOUND	# Set status to GAME_NOT_FOUND.

		elif game["status"] != "started":	# If game's status that is given in the dict is not started;
											# status may be 'aborted' or 'ended'. Both cases indicate
											# game does not continue.
			self.status =  GAME_NOT_LIVE	# Set status to GAME_NOT_LIVE

		else:
			moves = game["moves"]			 # Get already played moves. This is a string.

			self_moves_len = len(self.moves) # Get last played moves' string length.

			if len(moves) > self_moves_len:	 					# If new got moves string is longer than previous. 
																# This means new move is played.
				self.play_moves(moves[self_moves_len:].split())	# Play the new moves.
				self.moves = moves 		# Update moves.
				self.new_move = True	# Set new_move to True, because new moves are played.
			else:
				self.new_move = False	# Set False, since no new move is played.

			self.status = GAME_LIVE 	# Since game is not proven to be ended or aborted, status is set to GAME_LIVE.


	# Moves given moves that are given on the LiveGame object's board.
	# @param {List} moves A list of SAN type of move strings.
	# 
	# PROBLEM: If other move type different than SAN is passed, this won't work. But that is impossible for the time being.
	def play_moves(self, moves):
		for move in moves:
			self.board.push_san(move)


	# Returns a png image of the current situation of the board. Should be functional, yet to be used.
	# @return {PIL.Image} Png image of board.
	def get_board_image(self):
		return get_board_image(self.board)


	# Returns a representation of the current situation of the board that is made up of emotes.
	# @return {str} Board's representation consisting of emotes. 
	def get_board_emote_message(self):
		return get_board_emote_message(self.board)


	# Returns the new representation of the board if there's any new moves. Else returns warning.
	# @return {str|WARNING_ID=int} New representation of the board, or warning.  
	def get_update_message(self):
		self.update_game()	# Update the game before updating the message.

		if self.status == GAME_LIVE:	# If game is still going on.
			if self.new_move:			# If any new move is played.
				update_message = self.get_board_emote_message()	# Get new message content.
			else:
				update_message = NO_NEW_MOVE # If no new move is played return NO_NEW_MOVE.
		else:	# If game is not going on.
			update_message = self.message.content + "\n\nGame ended."

		return update_message


# Gets the chess game with the given id. Then returns it.
# @param 	{str}	Id of a chess game that is played on lichess. 
# @return 	{dict}	The dictionary that contains information about the game.
def get_game_with_id(game_id):

	try:
		game = lichess.api.game(game_id)
	except lichess.api.ApiHttpError:
		game = GAME_NOT_FOUND

	return game


# Gets a list of games of given player, starting from last played to first played.
def get_player_games(player_name, n=1):

	try:
		games = lichess.api.user_games(player_name, max=n)

	except lichess.api.ApiHttpError:
		games = ACCOUNT_NOT_FOUND

	return games


def get_board_png_bytes(board):
	return BytesIO(cairosvg.svg2png(chess.svg.board(board)))


def get_board_image(board):

	stream = get_board_png_bytes(board)
	image  = Image.open(stream).convert("RGBA")
	stream.close()

	return image


def get_board_emote_message(board):

	board_string = str(board).replace(" ", "")

	emote_message = ""

	for i in range(len(board_string)):

		if board_string[i]  == "\n":
			emote_message += "\n"
		elif board_string[i] == ".":
			emote_message += EMOTE_PIECE_SYMBOLS[i%2]
		else:
			emote_message += EMOTE_PIECE_SYMBOLS[f"{board_string[i]}{i%2}"]

	return emote_message


def get_fen_emote_message(fen):

	if fen != None:
		board = chess.Board(fen)
	else:
		board = chess.Board()

	return get_board_emote_message(board)


def get_command_args(message):
	return message.content.split()[1:]


def get_player_statistics(player_name):

	try:
		player_statistics = lichess.api.user(player_name)
	except lichess.api.ApiHttpError:
		player_statistics = ACCOUNT_NOT_FOUND

	return player_statistics


def get_player_statistics_embed(player_name):

	embed = ACCOUNT_NOT_FOUND
	player_statistics_dict = get_player_statistics(player_name)

	if player_statistics_dict != ACCOUNT_NOT_FOUND:

		if "closed" not in player_statistics_dict:

			color  = DISCORD_GREEN if player_statistics_dict["online"] else discord.Embed.Empty

			embed_title = f"{player_name.title()}"

			perfs = player_statistics_dict["perfs"]
			count = player_statistics_dict["count"]
			
			bio = ""
			try:
				bio = player_statistics_dict["profile"]["bio"] + "\n"
			except KeyError:
				pass

			currently_playing = ""

			if "playing" in player_statistics_dict:
				currently_playing = f"Currently Playing: {player_statistics_dict['playing']}\n"

			last_played = get_player_games(player_name, 1)

			try:
				last_played = f"Last Played: https://lichess.org/{next(last_played)['id']}\n"
			except StopIteration:
				last_played = ""

			count_keys = list(count.keys())
			count_values = list(count.values())

			ratings_str = ""
			numbers_str = ""

			ratings = [f"•{k.title()}: {perfs[k]['rating']}\n" for k in perfs]
			numbers = [f"•{count_keys[i].title()}: {count_values[i]}\n" for i in range(8) if count_keys[i][-1] != 'H']

			for s in ratings:
				ratings_str += s

			for s in numbers:
				numbers_str += s

			url = player_statistics_dict["url"]
			
			stats = """{}
			{}{}
			Ratings
			{}
			Number of Games
			{}
			Account: {}
			""".format(bio, currently_playing, last_played, ratings_str, numbers_str, url)

			embed = discord.Embed(title=embed_title, description=stats, colour=color)

		else:
			embed = ACCOUNT_CLOSED

	return embed


def get_command_info(command):
	
	command_usage = COMMAND_NOT_FOUND
	command_explanation = COMMAND_NOT_FOUND

	try:
		command_usage  = command_usages[command]
		command_explanation = command_explanations[command]
	except KeyError:
		pass

	return (command_usage, command_explanation)


async def update_live_games():
	while True:
		for game in live_games:
			
			update_message = game.get_update_message()

			if update_message != NO_NEW_MOVE:

				try:
					await game.message.edit(content=update_message)
				except AttributeError:
					pass

			if game.status != GAME_LIVE:
				live_games.remove(game)
		
		await asyncio.sleep(LIVE_GAMES_REFRESH_RATE)


### COMMAND FUNCTIONS ###/

def return_message_gif(message, game_id):

	game = get_game_with_id(game_id)
	answer = ""

	if game == GAME_NOT_FOUND:
		answer = f"No game with id `{game_id}` is found."

	elif game["status"] == "started":
		answer = f"Game with id `{game_id}` has not ended yet. Use `watch` command instead."

	else:
		answer = f"https://lichess1.org/game/export/gif/{game_id}.gif"

	return message.channel.send(answer)


def return_message_help(message, command="help"):

	command_info = get_command_info(command)

	if COMMAND_NOT_FOUND not in command_info:
		answer = "`{}`\n{}".format(*command_info)
		answer += f"\nCommands: `{list(command_usages.keys())}`" if command == "help" else ""
	else:
		answer = f"Command {command} does not exist. Use `{COMMAND_PREFIX} help` to see commands."	

	return message.channel.send(answer)


def return_message_user(message, user_name):

	answer = f"No user found with username `{user_name}`."

	embed = get_player_statistics_embed(user_name)

	if embed == ACCOUNT_CLOSED:
		answer = f"Account is closed."
	elif embed != ACCOUNT_NOT_FOUND:
		return message.channel.send(embed=embed)

	return message.channel.send(answer)


def return_message_watch_game(message, game_id):

	if game_id not in live_games:
		game = LiveGame(game_id)

		if game.status == GAME_LIVE:

			game_info_dict = get_game_with_id(game_id)

			#game_info_message = message.channel.send(f"{game_info_dict['players']['white']['user']['name']} vs {game_info_dict['players']['black']['user']['name']}\n")

			game_emote_message = message.channel.send(game.get_board_emote_message())

			live_games.append(game)

			return game_emote_message
		
		elif game.status == GAME_NOT_LIVE:
			return message.channel.send(f"Game with id `{game_id}` is not live anymore. Use `{COMMAND_PREFIX} gif {game_id}` instead.")

		elif game.status == GAME_NOT_FOUND:
			return message.channel.send(f"No game was found with id `{game_id}`")
	else:
		return message.channel.send(f"Game with id `{game_id}` is already being watched.")

def return_message_tv(message, game_type):

	try:
		game_id = lichess.api.tv_channels()[game_type.title()]["gameId"]

		return return_message_watch_game(message, game_id)

	except KeyError:
		return message.channel.send(f"{game_type} is not a real game type.")


def return_message_emote_fen(message, fen=None):
	return message.channel.send(get_fen_emote_message(fen))

### COMMAND FUNCTIONS ###


command_functions = {
	"help" : return_message_help,
	"gif"  : return_message_gif,
	"user" : return_message_user,
	"watch": return_message_watch_game,
	"tv"   : return_message_tv,
}


def manage_commands(message):

	args = get_command_args(message)
	arg_count = len(args)

	answer = ""

	try:
		return command_functions[args[0]](message, *args[1:])
	except KeyError:
		answer = f"`{args[0]}` is not an existing command."
	except TypeError:
		answer = f"Not enough arguments were given. See `{COMMAND_PREFIX} help {args[0]}`"
	except IndexError:
		return command_functions["help"](message)

	return message.channel.send(answer)


@client.event
async def on_ready():
	print('Logged in as {0.user}'.format(client))
	client.loop.create_task(update_live_games())

@client.event
async def on_message(message):
	if message.author == client.user:
		
		if message.content.startswith("<:"):
			live_games[-1].message=message

	elif message.content.startswith(COMMAND_PREFIX):
		answers = manage_commands(message)

		if type(answers) == tuple:
			for a in answers:
				await a
		else:
			await answers

client.run(token)


