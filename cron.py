import webapp2
import logging
from models import Player, Team, TeamApplication
from google.appengine.ext import ndb
from gameconfig import EnergyConfig


class EnergyTickHandler(webapp2.RequestHandler):
    def get(self):
        players = Player.query(Player.energy < EnergyConfig.maxEnergy)

        for player in players:
            player.energy += EnergyConfig.tickAmount
            if player.energy > EnergyConfig.maxEnergy:
                player.energy = EnergyConfig.maxEnergy
            player.put()

class RankedTeamGamesHandler(webapp2.RequestHandler):
    def get(self):
        logging.info('Run ranked team games')

app = webapp2.WSGIApplication([
    (r'/cron/energy_tick', EnergyTickHandler),
    (r'/cron/run_ranked_team_games', RankedTeamGamesHandler)
], debug=True)
