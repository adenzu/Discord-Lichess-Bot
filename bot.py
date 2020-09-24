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

# This dictionary is for converting pychess board ASCII graphic to discord emote-image-thingy.
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
# PROBLEM:	The emote representation of board is created from scratch whenever there's 
#			a new move to edit the message, not efficient.
# SOLUTION:	Emote representation of the board can be stored in a 2D array, and altered
#			just slightly for the new moves.
class LiveGame:

	# @param {str} game_id An id of a chess game that is played on lichess.
	def __init__(self, game_id):

		self.game_id  = game_id			# Stores its game id, since lichess.api returns not an object for a game
										# but a dictionary for current status for it, this will be needed.  
		self.board    = chess.Board()	# Initializes new chess board for the game. 
		self.moves    = ""				# Contains all the moves that is played til now.
		self.message  = None			# Whenever a new move is played, the message that contains game's 
										# representation (consisting of emotes) has to be updated, thus
										# has to be stored to be edited later.
		self.new_move = False

		self.update_game()	# To create new needed variables and update existing ones.


	# Equality result is dependant on the game's id. Not the object itself.
	# @param	{_}			other	The other value in the equality operation.
	# @return	{boolean}			The result of logical equality operation.
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

			if len(moves) > self_moves_len:						# If new got moves string is longer than previous. 
																# This means new move is played.
				self.play_moves(moves[self_moves_len:].split())	# Play the new moves.
				self.moves = moves		# Update moves.
				self.new_move = True	# Set new_move to True, because new moves are played.
			else:
				self.new_move = False	# Set False, since no new move is played.

			self.status = GAME_LIVE		# Since game is not proven to be ended or aborted, status is set to GAME_LIVE.


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
# @param	{str}	game_id	Id of a chess game that is played on lichess. 
# @return	{dict}			The dictionary that contains information about the game.
def get_game_with_id(game_id):

	try:
		game = lichess.api.game(game_id)
	except lichess.api.ApiHttpError:
		game = GAME_NOT_FOUND

	return game


# Gets a list of games of given player, sorted as from last played to first played.
# @param	{str}		player_name		User name of the chess player.
# @param	{int}		n				Number of games that will be pulled.
# @return	{generator|WARNING_ID=int}	A generator that will return one game at a time.
def get_player_games(player_name, n=1):

	try:
		games = lichess.api.user_games(player_name, max=n)

	except lichess.api.ApiHttpError:
		games = ACCOUNT_NOT_FOUND

	return games


# Returns the png image byte stream of given board's current state.
# @param	{chess.Board}	board	The board whose image byte stream will be generated.
# @return	{_io.BytesIO}			Byte stream that corresponds to the image.
def get_board_png_bytes(board):
	return BytesIO(cairosvg.svg2png(chess.svg.board(board)))


# Gets image byte stream of given board then creates the image and returns it.
# @param	{chess.Board}	board	The board whose image will be generated.
# @return	{PIL.Image}				The png image of the board's current state.
def get_board_image(board):

	stream = get_board_png_bytes(board)
	image  = Image.open(stream).convert("RGBA")
	stream.close()

	return image


# Returns given board's emote-representation string.
# @param	{chess.Board}	board				The board whose emote-representation will be generated.
# @return	{str}			emote_message		Emote-representation of the given board.
def get_board_emote_message(board):

	board_string = str(board).replace(" ", "")	# str(chess.Board) returns a ASCII like representation
												# of the board (see more at their website). Spaces are
												# unnecessary thus removed. 

	emote_message = ""

	# Chess board is made up of 2 different colored squares.
	# And same colored squares should be diagonal to each other,
	# to achieve this 0 corresponds to white square and 1 is for black,
	# iteration is numerical not element based thus iteration variable i
	# is used for determining current square's color. Different
	# row start square color is dealt automatically since '\n' characters
	# are also in the string and thus affect the iteration variable.
	for i in range(len(board_string)):

		if board_string[i]  == "\n":
			emote_message += "\n"
		elif board_string[i] == ".":	# '.' corresponds to blank square.
			emote_message += EMOTE_PIECE_SYMBOLS[i%2]
		else:
			emote_message += EMOTE_PIECE_SYMBOLS[f"{board_string[i]}{i%2}"]

	return emote_message


# Returns emote-representation of given fen, this function is currently not used.
# @param	{str}	fen	Any possible chess game fen.
# @return	{str}		Emote-representation of given fen.
def get_fen_emote_message(fen):
	return get_board_emote_message(chess.Board(fen))


# Seperates user command to parameters, then returns the parameter list.
# @param	{discord.Message}	message	Any discord message.
# @return	{list}						Command parameters in the message.
def get_command_args(message):
	return message.content.split()[1:]


# Gets information about given player, then returns it. If not found, returns warning.
# @param	{str}					player_name			User name of a player on lichess.
# @return	{dict|WARNING_ID=int}	player_statistics	Dictionary of user's information.
def get_player_statistics(player_name):

	try:
		player_statistics = lichess.api.user(player_name)
	except lichess.api.ApiHttpError:
		player_statistics = ACCOUNT_NOT_FOUND

	return player_statistics


# Creates an embed with information of the player with given name. Then returns it. Will return warning 
# when process is not done properly.
# @param	{str}							player_name	User name of a player on lichess.
# @return	{discord.Embed|WARNING_ID=int}				Embed that includes information about the player.
def get_player_statistics_embed(player_name):

	embed = ACCOUNT_NOT_FOUND									# Set to warning initially.
	player_statistics_dict = get_player_statistics(player_name)	# Get info about player.

	if player_statistics_dict != ACCOUNT_NOT_FOUND:	# If user is found.

		if "closed" not in player_statistics_dict:	# Accounts can be closed, and when they are
													# lichess api returns a dictionary that has 
													# 'closed' as a key in it.

			# Color of the embed, green if user is online at the moment, blank if not.
			color  = DISCORD_GREEN if player_statistics_dict["online"] else discord.Embed.Empty

			embed_title = f"{player_name.title()}"	# Embed's title is the palyer's user name.

			perfs = player_statistics_dict["perfs"]	# Player's ranking of game types.
			count = player_statistics_dict["count"]	# Player's number of games.
			
			# If user has a biography then include it too.
			try:
				bio = player_statistics_dict["profile"]["bio"] + "\n"
			except KeyError:
				bio = ""

			# Alco include current game that the player is playing, if any.
			currently_playing = ""
			if "playing" in player_statistics_dict:
				currently_playing = f"Currently Playing: {player_statistics_dict['playing']}\n"

			# Get last played game to include also, if there's any.
			last_played = get_player_games(player_name, 1)
			try:
				last_played = f"Last Played: https://lichess.org/{next(last_played)['id']}\n"
			except StopIteration:
				last_played = ""

			# Seperating keys and values, this way it's easier to iterate and form the string for info.
			count_keys = list(count.keys())
			count_values = list(count.values())

			ratings_str = ""
			numbers_str = ""

			# Getting stats of the player.
			ratings = [f"•{k.title()}: {perfs[k]['rating']}\n" for k in perfs]
			numbers = [f"•{count_keys[i].title()}: {count_values[i]}\n" for i in range(8) if count_keys[i][-1] != 'H']

			# Turning lists into string. FIX: this would be better if there's a function for this. (list->str conversion)
			for s in ratings:
				ratings_str += s

			for s in numbers:
				numbers_str += s

			# Link to the user's profile.
			url = player_statistics_dict["url"]
			
			# Final string for the embed.
			stats = """{}
			{}{}
			Ratings
			{}
			Number of Games
			{}
			Account: {}
			""".format(bio, currently_playing, last_played, ratings_str, numbers_str, url)

			# Create embed.
			embed = discord.Embed(title=embed_title, description=stats, colour=color)

		else:	# If account is closed then return this warning.
			embed = ACCOUNT_CLOSED

	return embed


# Returns information and explanation about given command.
# @param	{str}	command	Any command that this bot can execute.
# @return	{tuple}			Two strings. First one is usage of command, second is explanation.
def get_command_info(command):
	
	try:				# Try getting info about the command.
		command_usage  = command_usages[command]
		command_explanation = command_explanations[command]
	except KeyError:	# Return warning if failed.
		command_usage = COMMAND_NOT_FOUND
		command_explanation = COMMAND_NOT_FOUND

	return (command_usage, command_explanation)


# Updates messages that are for live games.
# 
# PROBLEM: My knowledge about async is shallow. Codes here may not be good practice.
async def update_live_games():
	while True:

		# For every live game.
		for game in live_games:
			
			update_message = game.get_update_message()	# Get new message for representing the board.

			if update_message != NO_NEW_MOVE:	# If there are new moves.

				# Try editing message. If it fails pass, the cause of this
				# error is currently unknown.
				try:
					await game.message.edit(content=update_message)
				except AttributeError:
					pass

			if game.status != GAME_LIVE:	# If the game ended.
				live_games.remove(game)		# Remove it from the list.
		
		await asyncio.sleep(LIVE_GAMES_REFRESH_RATE)	# Wait for the next check.




### COMMAND FUNCTIONS ###/

# Bot commands have their own functions. Whenever a new command is added a function for that command 
# is also added. The function and the command is linked together via dictionary command_functions.


# Sends gif of the game with given id. This is a response to the command 'gif'.
# @param	{discord.Message}	message	The message that triggered this function.
# @param	{string}			game_id	Id of the chess game that is played on lichess.
# @return	{discord.Message}			The message that includes the gif of the game.
def return_message_gif(message, game_id):

	game = get_game_with_id(game_id)	# Get game info.

	if game == GAME_NOT_FOUND:			# If it's not found.
		response = f"No game with id `{game_id}` is found."

	elif game["status"] == "started":	# If game is not ended yet.
		response = f"Game with id `{game_id}` has not ended yet. Use `watch` command instead."

	else:	# Lichess already generates gif of games. So the only thing needed is sending the link to that gif.
		response = f"https://lichess1.org/game/export/gif/{game_id}.gif"

	return message.channel.send(response)


# Sends explanation of given command. This is a response to the command 'help'.
# @param	{discord.Message}	message	The message that triggered this function.
# @param	{string}			command	The command that is wanted to be explained. If not specified, it's set to 'help'.
# @return	{discord.Message}			The message that includes command explanation.
def return_message_help(message, command="help"):

	command_info = get_command_info(command)

	if COMMAND_NOT_FOUND not in command_info:		# If command is found.
		response = "`{}`\n{}".format(*command_info)	# Explanation.
		response += f"\nCommands: `{list(command_usages.keys())}`" if command == "help" else ""	# If command in question is 'help'
																								# then show all the existing commands.
																								# Not the prettiest looking way of doing this.
	else:
		response = f"Command {command} does not exist. Use `{COMMAND_PREFIX} help` to see commands."	# If command does not exist
																										# tell the user so.

	return message.channel.send(response)


# Sends information about the user on lichess with the given user name. This is a response to the command 'user'.
# @param	{discord.Message}	message		The message that triggered this function.
# @param	{string}			user_name	The user name of the user that is wanted information on. 
# @return	{discord.Message}				The message that includes information about the user in question.
def return_message_user(message, user_name):

	# Initially set to a warning message.
	response = f"No user found with username `{user_name}`."

	embed = get_player_statistics_embed(user_name)	# Get info.

	if embed == ACCOUNT_CLOSED:					# If account is closed.
		response = f"Account is closed."			# Tell so.
	elif embed != ACCOUNT_NOT_FOUND:			# If not found. Thus initial response.
		return message.channel.send(embed=embed)	# Else send the info.

	return message.channel.send(response)


# Sends message that shows the live game with given id. This is a response to the command 'watch'.
# @param	{discord.Message}	message		The message that triggered this function.
# @param	{string}			user_name	The user name of the user that is wanted information on. 
# @return	{discord.Message}				The message that has the emote-representation of the live game.
# 
# PROBLEM:	Needs more information about the game. Currently only the board is shown.
# PROBLEM:	Can't show live games with gif or images since they are not ended.
# 			Thus emotes are used, but this way the board is too small.
# PROBLEM:	When an already watched game is demanded sends a message that tells that the mentioned game
# 			is already being watched. But for the time being this doesn't really checks
# 			if the mentioned game is watched in the same discord server. This is not healthy.
def return_message_watch_game(message, game_id):

	if game_id not in live_games:	# Check if game is already being watched.
		game = LiveGame(game_id)	# Create game.

		if game.status == GAME_LIVE:	# Check if game is still going on. 
										# PROBLEM:	Creating the class object for the game
										# 			before checking if game is still going on
										# 			is not healthy. Should be done in reverse
										# 			order.

			game_info_dict = get_game_with_id(game_id)	# Get info.

			game_emote_message = message.channel.send(game.get_board_emote_message())	# Create the message.

			#	game_emote_message is supposed to be linked to the game.
			#	But if it's done by game.message = game_emote_message right here,
			#	then it's linked as a coroutine object. This is a problem.
			#	It has to be linked after the message is sent. This is done checking messages
			#	that the bot sent itself. If it starts with '<:' then that's an emote and thus
			#	(for the time being) that message can only be the message that shows
			#	a live game. Then that message is linked to the last game that is added
			#	to the list live_games. 
			#	THIS IS NOT EFFICIENT OR EVEN LOGICAL AT ALL. THERE HAS TO BE A BETTER WAY. 

			live_games.append(game)	# Add game to the list.

			return game_emote_message
		
		elif game.status == GAME_NOT_LIVE:	# If game is not live anymore.
			return message.channel.send(f"Game with id `{game_id}` is not live anymore. Use `{COMMAND_PREFIX} gif {game_id}` instead.")

		elif game.status == GAME_NOT_FOUND: # If game is not found.
			return message.channel.send(f"No game was found with id `{game_id}`")
	else:	# Game is being watched. Won't create a new message for it.
		return message.channel.send(f"Game with id `{game_id}` is already being watched.")


# Sends message that shows the live game that is shown on lichess tv with given game type. This is a response to the command 'tv'.
# @param	{discord.Message}	message		The message that triggered this function.
# @param	{string}			game_type	The game type that is wanted to be watched (e.g Blitz). 
# @return	{discord.Message}				The message that has the emote-representation of the live game.
def return_message_tv(message, game_type):

	try:
		game_id = lichess.api.tv_channels()[game_type.title()]["gameId"]
		return return_message_watch_game(message, game_id)

	except KeyError:
		return message.channel.send(f"{game_type} is not a real game type.")


### COMMAND FUNCTIONS ###



# Commands and their functions.
command_functions = {
	"help" : return_message_help,
	"gif"  : return_message_gif,
	"user" : return_message_user,
	"watch": return_message_watch_game,
	"tv"   : return_message_tv,
}


# Executes command functions. Returns their response.
# @param	{discord.Message}	message	Any message starting with command prefix that it's author is not this bot.
def manage_commands(message):

	args = get_command_args(message)	# Get parameters.

	try:
		return command_functions[args[0]](message, *args[1:])	# Run the function that is related to the command.
	except KeyError:											# If command is not found in existing commands.
		response = f"`{args[0]}` is not an existing command."	# Tell so.
	except TypeError:											# Else if parameters are not enough. 
		response = f"Not enough parameters were given. See `{COMMAND_PREFIX} help {args[0]}`"
	except IndexError:	# If command wasn't manageable.
		return command_functions["help"](message)

	return message.channel.send(response)


@client.event
async def on_ready():
	print('Logged in as {0.user}'.format(client))
	client.loop.create_task(update_live_games())	# Create a loop check for live games.

@client.event
async def on_message(message):
	if message.author == client.user:
		
		if message.content.startswith("<:"):	# If this message starts with emote.
			live_games[-1].message=message		# Then has to be emote-representation of a live game. Link it. See 498.

	# If any user other than this bot sent a command.
	elif message.content.startswith(COMMAND_PREFIX):
		responses = manage_commands(message)	# Get response for the command.

		if type(responses) == tuple:	# If more than one responses were created.
			for r in responses:
				await r	# Send response message.
		else:
			await responses	# Send response message.

client.run(token)


