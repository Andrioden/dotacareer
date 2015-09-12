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

        ndb.get_context().clear_cache() # If it is not cleared the following count of queued players wont count this
        match_queue = match_queue_key.get()
        self._notify_players_new_queue_size(match_queue.type)
        set_json_response(self.response, {'doing': match_queue.get_data()})

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