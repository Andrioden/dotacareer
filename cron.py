import webapp2
import logging
from models import Player, Team, TeamMatch, MatchSoloQueue, Match, MatchPlayer
from google.appengine.ext import ndb
from gameconfig import EnergyConfig, CashConfig
import datetime
from api.utils import is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue

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
            match.setup_soloqueue_match(players)
            ndb.delete_multi([queue.key for queue in match_solo_queues])
            for player in players:
                player.doing = match.key
                player.put()
                player.websocket_notify("MatchFound", match.get_data())


class TeamMatchmakingHandler(webapp2.RequestHandler):
    def get(self):
        now_hour = datetime.datetime.now().hour
        eligible_teams = []
        for team in Team.query().order(Team.ranked_last_match).fetch():
            if not is_hour_in_start_end_time_range_adjusted_for_timezone_offset_issue(team.ranked_start_hour, team.ranked_end_hour, now_hour):
                continue
            if Player.query(Player.team == team.key, Player.doing == None).count() > 0: # Be aware that Player.doing == None will bug if you removed doing manually in dev console
                eligible_teams.append(team)

        while len(eligible_teams) >= 2:
            match = TeamMatch(type="TeamRanked")
            players = match.setup_team_match([eligible_teams.pop(), eligible_teams.pop()])
            for player in players:
                player.doing = match.key
                player.put()
                player.websocket_notify("MatchFound", match.get_data())


class FinishMatchesHandler(webapp2.RequestHandler):
    def get(self):
        for match in Match.query(Match.winning_faction == None, Match.date <= datetime.datetime.now()):
            match.play_match()
            for match_player in MatchPlayer.query(MatchPlayer.match == match.key):
                player = match_player.player.get()
                player.doing = None
                player.put()
                player.websocket_notify("MatchFinished", match.get_data("full"))




        # Cant use ndb to filter with two inequality checks http://stackoverflow.com/questions/2671587/appengine-filter-inequality-and-ordering-fails
        # So we do half the filtering with the query, and the other half with python
        # teams_with_ranked_time_now = [team for team in Team.query(Team.ranked_time_start <= datetime.time(now_hour)).fetch() if team.ranked_time_end.hour >= now_hour]
        # for team in teams_with_ranked_time_now:
        #     available_players = Player.query(Player.team == team.key, Player.doing == None)
        #     if available_players.count() > 0:




app = webapp2.WSGIApplication([
    (r'/cron/energy_tick', EnergyTickHandler),
    (r'/cron/cash_tick', CashTickHandler),
    (r'/cron/solo_queue_matchmaking', SoloQueueMatchmakingHandler),
    (r'/cron/team_matchmaking', TeamMatchmakingHandler),
    (r'/cron/finish_matches', FinishMatchesHandler),
], debug=True)
