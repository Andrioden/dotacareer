#!/usr/bin/env python

import webapp2
import json
import logging
from utils import *
from models import Player
from google.appengine.api import users


class RegisterHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        user = users.get_current_user()

        # VALIDATION
        if not validate_request_data(self.response, request_data, ['nick']):
            return
        if not validate_logged_inn(self.response):
            return
        if not self._validate_has_not_player_already(user):
            return

        # REGISTER PLAYER
        new_player = Player(
            userid=user.user_id(),
            nick=request_data['nick'],
            skill=10000
        ).put().get()

        set_json_response(self.response, new_player.get_data())

    def _validate_has_not_player_already(self, user):
        if Player.query(Player.userid == user.user_id()).count() > 0:
            error_400(self.response, "ERROR_HAS_PLAYER", "You can only register 1 player")
            return False
        else:
            return True


class MyHandler(webapp2.RequestHandler):
    def get(self):
        # VALIDATION
        if not validate_logged_inn(self.response):
            return

        # RETURN PLAYER
        user = users.get_current_user()
        player = Player.query(Player.userid == user.user_id()).get()

        if player:
            set_json_response(self.response, {'has_player': True, 'player': player.get_data('full')})
        else:
            set_json_response(self.response, {'has_player': False})


class StopDoingHandler(webapp2.RequestHandler):
    def post(self):
        player = current_user_player()
        player.clear_doing()

        set_json_response(self.response, {'code': "OK"})


app = webapp2.WSGIApplication([
    (r'/api/players/register', RegisterHandler),
    (r'/api/players/my', MyHandler),
    (r'/api/players/stopDoing', StopDoingHandler),
], debug=True)