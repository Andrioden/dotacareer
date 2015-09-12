import webapp2
import logging
from models import Player, Team, TeamApplication, MatchSoloQueue, Match
from google.appengine.ext import ndb
from gameconfig import EnergyConfig, CashConfig


class EnergyTickHandler(webapp2.RequestHandler):
    def get(self):
        players = Player.query(Player.energy < EnergyConfig.maxEnergy)

        for player in players:
            player.energy += EnergyConfig.tickAmount
            if player.energy > EnergyConfig.maxEnergy:
                player.energy = EnergyConfig.maxEnergy
            player.put()


class CashTickHandler(webapp2.RequestHandler):
    def get(self):
        players = Player.query()

        for player in players:
            player.cash += CashConfig.tickAmount
            player.put()


class SoloQueueMatchmakingHandler(webapp2.RequestHandler):
    def get(self):
        self._trigger_played_match("Ranked")
        self._trigger_played_match("Unranked")

    def _trigger_played_match(self, match_type):
        if MatchSoloQueue.query(MatchSoloQueue.type == match_type).count() >= 2:
            match_players = [match_queue.player.get() for match_queue in MatchSoloQueue.query(MatchSoloQueue.type == match_type).fetch(10)]
            match = Match(type=match_queue.type)
            match.play_match(match_players)
            for player in match_players:
                player.clear_doing()
                player.websocket_notify("MatchCompleted", match.get_data())


class RankedTeamGamesHandler(webapp2.RequestHandler):
    def get(self):
        teams = Team.query(Team.play_ranked == True)
        logging.info("Number of teams: %s" % teams.count())
        # Must implement team play match


app = webapp2.WSGIApplication([
    (r'/cron/energy_tick', EnergyTickHandler),
    (r'/cron/cash_tick', CashTickHandler),
    (r'/cron/solo_queue_matchmaking', SoloQueueMatchmakingHandler),
    (r'/cron/run_ranked_team_games', RankedTeamGamesHandler),

], debug=True)
