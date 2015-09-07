#!/usr/bin/env python

import webapp2
import logging
from utils import *
from google.appengine.api import users
from models import MatchSoloQueue, Match
from google.appengine.ext import ndb


class JoinSoloQueueHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()

        # VALIDATION
        if not validate_request_data(self.response, request_data, ['type']):
            return
        if player.doing:
            error_400(self.response, "ERROR_PLAYER_BUSY", "Player is busy.")
            return

        # JOIN QUEUE
        match_queue_key = MatchSoloQueue(
            player=player.key,
            type=request_data['type']
        ).put()

        player.doing = match_queue_key
        player.put()

        ndb.get_context().clear_cache() # If it isnt cleared the following count of queued players wont count this
        match_queue = match_queue_key.get()
        match = self._trigger_played_match(match_queue, player)
        if match:
            set_json_response(self.response, {'doing': None, 'match': match.get_data("full")})
        else:
            self._notify_players_new_queue_size(match_queue.type)
            set_json_response(self.response, {'doing': match_queue.get_data()})

    def _trigger_played_match(self, match_queue, request_player):
        if MatchSoloQueue.query(MatchSoloQueue.type == match_queue.type).count() >= 2:
            match_players = [match_queue.player.get() for match_queue in MatchSoloQueue.query(MatchSoloQueue.type == match_queue.type).fetch(10)]
            match = Match(type=match_queue.type)
            match.play_match(match_players)
            for player in match_players:
                player.clear_doing()
                if not player.key == request_player.key:
                    player.websocket_notify("MatchCompleted", match.get_data())
            return match
        else:
            return None

    def _notify_players_new_queue_size(self, match_queue_type):
        all_match_queues = MatchSoloQueue.query(MatchSoloQueue.type == match_queue_type)
        all_match_queues_count = all_match_queues.count()
        for match_queue in all_match_queues:
            match_queue.player.get().websocket_notify("NewPlayerDoingQueueCount", all_match_queues_count)


class PlayAgainstBotsHandler(webapp2.RequestHandler):
    def post(self):
        player = current_user_player()

        if player.doing:
            error_400(self.response, "ERROR_PLAYER_BUSY", "Player is busy.")
            return

        bot_match = Match(type="Bot")
        bot_match.play_bot_match(player)

        set_json_response(self.response, {'match': bot_match.get_data("full")})


class RESTHandler(webapp2.RequestHandler):
    def get(self, match_id):
        match = Match.get_by_id(int(match_id))
        set_json_response(self.response, match.get_data('full'))


app = webapp2.WSGIApplication([
    (r'/api/matches/playAgainstBots', PlayAgainstBotsHandler),
    (r'/api/matches/joinSoloQueue', JoinSoloQueueHandler),
    (r'/api/matches/rest/(\d+)', RESTHandler),
], debug=True)