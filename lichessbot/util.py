from lichessbot.exceptions import *
from lichessbot.config import *

import numpy as np
import time



async def send_message(channel, error_message):
	await channel.send(error_message)


async def handle_error(message, error):

	try:
		await send_message(message.channel, error.message)
	except KeyError:
		await send_message(message.channel, f"Unknown error: `{error}`\nCaused by: `{message}`")


def seconds_conversion(seconds):
	return dict(zip(["years", "months", "days", "hours", "minutes", "seconds"], (np.array(time.gmtime(seconds)) - np.array(time.gmtime(0)))[:-3]))
