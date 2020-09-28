from lichessbot.client import *
from lichessbot.config import *


import numpy as np
import asyncio
import chess



ongoing_games = []

async def update_live_games():
	while True:

		for live_game in ongoing_games:
			await live_game.update_game()

		await asyncio.sleep(LIVE_GAME_REFRESH_RATE)


class LiveGame:

	def __init__(self, game_id):

		self.game_id = game_id

		self.board = chess.Board()
		
		self.board_message = None
		self.white_message = None
		self.black_message = None

		self.game_info = None
		self.move_count = 0
		self.penalty_time = 0
		self.check_since_last_move = 0

		ongoing_games.append(self)

	def get_game_info(self):
		self.game_info = client.games.export(self.game_id)
		return self.game_info

	def get_move(self):
		return self.get_game_info()["moves"]

	def get_move_list(self):
		return self.get_move().split()

	def play_moves(self, move_list):

		uci_equals = []

		for move in move_list:
			uci_equals.append(str(self.board.push_san(move)))

		return uci_equals

	def get_emote_representation(self):

		i = 0

		emote_representation = ""

		for square in str(self.board).replace(" ", ""):
			if square != "\n":
				emote_representation += EMOTE_PIECE_SYMBOLS[f"{square}{i%2}"]
			else:
				emote_representation += "\n"
			i+=1

		return emote_representation

	async def update_message(self):

		try:
			await self.board_message.edit(content=f"{self.black_message}\n{self.get_emote_representation()}\n{self.white_message}")
		except AttributeError:
			return

	async def update_game(self):

		self.penalty_time -= LIVE_GAME_REFRESH_RATE

		try:
			if self.penalty_time <= 0: 
				moves = self.get_move_list()

				if len(moves) > self.move_count:
					
					self.check_since_last_move = 0

					new_moves = moves[self.move_count:]
					self.move_count = len(moves)

					self.play_moves(new_moves)

					await self.update_message()
				
				else:

					self.check_since_last_move += 1
					self.penalty_time = self.check_since_last_move**.5 * LIVE_GAME_REFRESH_RATE
			else:
				return

		except berserk.exceptions.ResponseError:
			self.penalty_time = 60
			return

		if self.game_info["status"] != "started":
			await self.board_message.edit(content=f"{self.board_message.content }\n\nGame ended.")
			ongoing_games.remove(self)
