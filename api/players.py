#!/usr/bin/env python

import webapp2
import json
import logging
from utils import *
from models import Player, PlayerConfig
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


class NewConfigHandler(webapp2.RequestHandler):
    def post(self):
        player = current_user_player()
        new_config = PlayerConfig(player=player.key).put().get()
        set_json_response(self.response, new_config.get_data())


class UpdateConfigHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        config = PlayerConfig.get_by_id(int(request_data['id']))

        # VALIDATION
        if not config.player == player.key:
            error_400(self.response, "ERROR_NOT_YOUR_PLAYER", "You cant update another players config. You api-hacking or what?")
            return
        if not validate_request_data(self.response, request_data, ['name', 'farm_weight', 'gank_weight', 'push_weight']):
            return

        # UPDATE
        config.name = request_data['name']
        config.farm_weight = int(request_data['farm_weight'])
        config.gank_weight = int(request_data['gank_weight'])
        config.push_weight = int(request_data['push_weight'])
        config.put()

        set_json_response(self.response, {'code': "OK"})


class DeleteConfigHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        config = PlayerConfig.get_by_id(int(request_data['id']))

        # VALIDATION
        if not config.player == player.key:
            error_400(self.response, "ERROR_NOT_YOUR_PLAYER", "You cant delete another players config. You api-hacking or what?")
            return

        # DELETE
        config.key.delete()

        set_json_response(self.response, {'code': "OK"})


class SetActiveConfigHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        config = PlayerConfig.get_by_id(int(request_data['id']))

        # VALIDATION
        if not config.player == player.key:
            error_400(self.response, "ERROR_NOT_YOUR_PLAYER", "You cant delete another players config. You api-hacking or what?")
            return

        # UPDATE
        for active_config in PlayerConfig.query(PlayerConfig.player == player.key, PlayerConfig.active == True).fetch():
            active_config.active = False
            active_config.put()

        config.active = True
        config.put()

        set_json_response(self.response, {'code': "OK"})

app = webapp2.WSGIApplication([
    (r'/api/players/register', RegisterHandler),
    (r'/api/players/my', MyHandler),
    (r'/api/players/stopDoing', StopDoingHandler),
    (r'/api/players/newConfig', NewConfigHandler),
    (r'/api/players/updateConfig', UpdateConfigHandler),
    (r'/api/players/deleteConfig', DeleteConfigHandler),
    (r'/api/players/setActiveConfig', SetActiveConfigHandler),
], debug=True)