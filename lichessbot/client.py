import berserk

client  = berserk.Client()


def get_user_games(user_id):
	return client.games.export_by_player(user_id)
