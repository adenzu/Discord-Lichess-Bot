from lichessbot.config import LICHESS_TOKEN
import berserk

session = berserk.TokenSession(LICHESS_TOKEN)
client  = berserk.Client(session)


def get_user_games(user_id):
	return client.games.export_by_player(user_id)
