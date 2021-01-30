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


def seconds_conversion_text(seconds):

	time_string = ""
	equal_time = seconds_conversion(seconds)

	for time_type in equal_time:
		if equal_time[time_type]:
			time_string += f"{equal_time[time_type]} {time_type}"

	return time_string