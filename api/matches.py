#!/usr/bin/env python

import webapp2
import logging
from utils import *
from google.appengine.api import users
from models import MatchSoloQueue, Match


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

        match_queue = MatchSoloQueue(
            player=player.key,
            type=request_data['type']
        ).put()

        player.doing = match_queue
        player.put()

        set_json_response(self.response, player.doing.get().get_data())


class PlayAgainstBotsHandler(webapp2.RequestHandler):
    def post(self):
        player = current_user_player()

        bot_match = Match()
        bot_match.play_bot_match(player)

        return set_json_response(self.response, {'match': bot_match.get_data("full")})


class RESTHandler(webapp2.RequestHandler):
    def get(self, match_id):
        match = Match.get_by_id(int(match_id))
        set_json_response(self.response, match.get_data('full'))

app = webapp2.WSGIApplication([
    (r'/api/matches/playAgainstBots', PlayAgainstBotsHandler),
    (r'/api/matches/joinSoloQueue', JoinSoloQueueHandler),
    (r'/api/matches/rest/(\d+)', RESTHandler),
], debug=True)