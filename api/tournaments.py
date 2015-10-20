#!/usr/bin/env python

import logging
import webapp2
from models import Tournament
from utils import *


class TournamentsHandler(webapp2.RequestHandler):
    def get(self):
        set_json_response(self.response, [tournament.get_data() for tournament in Tournament.query()])


class JoinHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        team_key = player.team
        tournament = Tournament.get_by_id(int(request_data['tournament_id']))

        if team_key in tournament.participants:
            error_400(self.response, "ERROR_ALREADY_IN_TOURNAMENT", "Your team has already joined the tournament '%s'" % tournament.name)
            return

        tournament.participants.append(team_key)
        tournament.put()

        set_json_response(self.response, {'code': "OK"})

app = webapp2.WSGIApplication([
    (r'/api/tournaments/rest/', TournamentsHandler),
    (r'/api/tournaments/join/', JoinHandler)
], debug=True)
