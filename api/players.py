#!/usr/bin/env python

import webapp2
import json
import logging
from utils import error_400, validate_logged_inn, validate_request_data
from models import Player
from google.appengine.api import users


class Register(webapp2.RequestHandler):
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
            skill=10
        ).put().get()

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(new_player.get_data()))

    def _validate_has_not_player_already(self, user):
        if Player.query(Player.userid == user.user_id()).count() > 0:
            error_400(self.response, "ERROR_HAS_PLAYER", "You can only register 1 player")
            return False
        else:
            return True


class My(webapp2.RequestHandler):
    def get(self):
        # VALIDATION
        if not validate_logged_inn(self.response):
            return

        # RETURN PLAYER
        user = users.get_current_user()
        player = Player.query(Player.userid == user.user_id()).get()

        self.response.headers['Content-Type'] = 'application/json'
        if player:
            self.response.out.write(json.dumps({'has_player': True, 'player': player.get_data('full')}))
        else:
            self.response.out.write(json.dumps({'has_player': False}))

app = webapp2.WSGIApplication([
    (r'/api/players/register', Register),
    (r'/api/players/my', My),
], debug=True)