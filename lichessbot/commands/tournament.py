from lichessbot.command import Command
from lichessbot.exceptions import *
from lichessbot.parameter import *
from lichessbot.config import *
from lichessbot.client import *
from lichessbot.util import *

import discord


class CommandTournament(Command):

	name = "tournament"
	help_string = "View ongoing tournaments or view a specified tournament."
	aliases = []
	parameters = [ParamTournamentID(required=False)]
	enabled = False

	@classmethod
	async def run(cls, command_call):

		tournaments = client.tournaments.get()
		tournament_id = command_call.args[0]

		if tournament_id:
			
			try:
				path = f'api/tournament/{tournament_id}/results'
				params = {'nb': None}
				participant_iter = client.tournaments._r.get(path, params=params, stream=True)
			except berserk.exceptions.ResponseError:
				await command_call.channel.send(f"No tournament exist with id `{tournament_id}`.")
				return 
			
			tournament_info = client.tournaments._r.get(f"api/tournament/{tournament_id}")
			tournament_url  = f"https://lichess.org/tournament/{tournament_id}"

			embed_text = ""

			for key in tournament_info:

				if "secondsToStart" == key:
					embed_text = f"{seconds_conversion_text(tournament_info['secondsToStart'])} until the tournament begins.\n"
					break
				elif "secondsToFinish" == key:
					embed_text = f"{seconds_conversion_text(tournament_info['secondsToFinish'])} until the tournament ends.\n"
					break

			for i in range(10):

				participant_info = next(participant_iter)
				embed_text += f"{i + 1}) {participant_info['username']} {participant_info['rating']}".ljust(30) + f"{participant_info['score']}\n".rjust(5)

			embed = discord.Embed(title=tournament_info["fullName"], description=embed_text, url=tournament_url)

			await command_call.channel.send(embed=embed)

		else:

			if len(tournaments["started"]):

				embed_text = "Tournament Name                  Number of Players\n\n" 

				for ongoing_tournament in tournaments["started"]:
					embed_text += f"[{ongoing_tournament['fullName']}](https://lichess.org/tournament/{ongoing_tournament['id']})".ljust(45) + f"{ongoing_tournament['nbPlayers']}\n".rjust(5)

				embed = discord.Embed(title="Ongoing Tournaments", description=embed_text, url="https://lichess.org/tournament")

				await command_call.channel.send(embed=embed)

			else:
				await command_call.channel.send(f"There's currently no ongoing tournament.")
