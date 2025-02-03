
from bot.guantlet.tournament.models import Tournament, TournamentStatus, Character


class Database:
    def __init__(self):
        self.name = "tournament.db"
        self.db = None

    async def initialize(self):
        