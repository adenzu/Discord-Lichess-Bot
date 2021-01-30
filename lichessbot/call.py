from lichessbot.exceptions import *
from lichessbot.config import *
from lichessbot.util import *

import traceback

class Call():

	def __init__(self, message):

		self.msg = message
		self.message = message
		self.channel = self.msg.channel

		self.guild = self.msg.guild

		self.mentions = self.msg.mentions

		self.string = message.content
		self.content = message.content

		self.author = message.author
		
		self.author_name = self.author.nick

		try:
			self.raw_args = self.content.split()[1:]
			self.command = self.raw_args.pop()
			self.args = []
			self.executed = False
		except IndexError:
			raise NoCommand


