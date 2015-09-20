import webapp2
import logging
from models import Player, Team, MatchSoloQueue, Match, MatchPlayer, Bet
from google.appengine.ext import ndb
from gameconfig import EnergyConfig, CashConfig
from datetime import datetime

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
            player.websocket_notify("CashChange", CashConfig.tickAmount)


class SoloQueueMatchmakingHandler(webapp2.RequestHandler):
    def get(self):
        self._trigger_played_match("Ranked")
        self._trigger_played_match("Unranked")

    def _trigger_played_match(self, match_type):
        if MatchSoloQueue.query(MatchSoloQueue.type == match_type).count() >= 2:
            match_solo_queues = [match_queue for match_queue in MatchSoloQueue.query(MatchSoloQueue.type == match_type).fetch(10)]
            players = [match_queue.player.get() for match_queue in match_solo_queues]
            match = Match(type=match_queue.type)
            match.setup_match(players)
            ndb.delete_multi([queue.key for queue in match_solo_queues])
            for player in players:
                player.doing = match.key
                player.put()
                player.websocket_notify("MatchFound", match.get_data())


class FinishMatchesHandler(webapp2.RequestHandler):
    def get(self):
        for match in Match.query(Match.winning_faction == None, Match.date <= datetime.now()):
            match.play_match()
            for match_player in MatchPlayer.query(MatchPlayer.match == match.key):
                player = match_player.player.get()
                player.doing = None
                player.put()
                player.websocket_notify("MatchFinished", match.get_data("full"))


class RankedTeamGamesHandler(webapp2.RequestHandler):
    def get(self):
        teams = Team.query(Team.play_ranked == True)
        logging.info("Number of teams: %s" % teams.count())
        # Must implement team play match


app = webapp2.WSGIApplication([
    (r'/cron/energy_tick', EnergyTickHandler),
    (r'/cron/cash_tick', CashTickHandler),
    (r'/cron/solo_queue_matchmaking', SoloQueueMatchmakingHandler),
    (r'/cron/finish_matches', FinishMatchesHandler),
    (r'/cron/run_ranked_team_games', RankedTeamGamesHandler),
], debug=True)
