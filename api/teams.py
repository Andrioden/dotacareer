#!/usr/bin/env python

import webapp2
import logging
import datetime
from utils import *
from models import Player, Team, TeamApplication
from google.appengine.ext import ndb


class RegisterHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()

        # VALIDATION
        if not validate_request_data(self.response, request_data, ['team_name']):
            return
        elif not validate_logged_inn(self.response):
            return
        elif not _validate_has_no_team(self.response, player):
            return

        # REGISTER TEAM
        new_team = Team(
            name=request_data['team_name'],
            owner=player.key
        ).put().get()

        # JOIN TEAM WITH PLAYER
        player.team = new_team.key
        player.put()

        ndb.get_context().clear_cache()  # Required to get the new player as part of the get_data
        set_json_response(self.response, {'team': new_team.get_data('full')})


class TeamsHandler(webapp2.RequestHandler):
    def get(self):
        set_json_response(self.response, [team.get_data() for team in Team.query().fetch()])


class SendApplicationHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        team_key = ndb.Key(Team, int(request_data['team_id']))

        # VALIDATIONS
        if not validate_request_data(self.response, request_data, ['team_id']):
            return
        elif not validate_logged_inn(self.response):
            return
        elif not _validate_has_no_team(self.response, player):
            return

        team_application = TeamApplication(
            team=team_key,
            player=player.key,
            text=request_data['text']
        ).put().get()

        _websocket_notify_team(team_key, 'Team_NewApplication', team_application.get_data())
        set_json_response(self.response, {'code': "OK"})


class AcceptApplicationHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        team_owner = current_user_player()
        application = TeamApplication.get_by_id(int(request_data['application_id']))
        team = application.team.get()

        # VALIDATIONS
        if not _validate_is_team_owner(self.response, team_owner, team):
            return

        # DO SHIT
        applicant = application.player.get()
        applicant.team = application.team
        applicant.put()
        application.key.delete()

        applicant.websocket_notify('Player_TeamApplicationAccepted', team.get_data("full"))
        _websocket_notify_team(team.key, 'Team_NewMember', applicant.get_data_nick_and_id())
        set_json_response(self.response, {'code': "OK"})


class DeclineApplicationHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        application = TeamApplication.get_by_id(int(request_data['application_id']))
        team = application.team.get()

        # VALIDATIONS
        if not _validate_is_team_owner(self.response, player, team):
            return

        # DO SHIT
        application.key.delete()

        _websocket_notify_team(team.key, 'Team_ApplicationDeclined', application.get_data())
        set_json_response(self.response, {'code': "OK"})


class KickMemberHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        kicked_player = Player.get_by_id(int(request_data['player_id']))
        team = kicked_player.team.get()

        # VALIDATIONS
        if not _validate_is_team_owner(self.response, player, team):
            return
        if player == kicked_player:
            error_400(self.response, "ERROR_CANT_KICK_SELF", "You cannot kick yourself from your own team. Are you retarded?")
            return

        # DO SHIT
        kicked_player.team = None
        kicked_player.put()

        kicked_player.websocket_notify('Player_KickedFromTeam')
        _websocket_notify_team(team.key, 'Team_KickedMember', kicked_player.get_data_nick_and_id())
        set_json_response(self.response, {'code': "OK"})


class UpdateConfigHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        player = current_user_player()
        team = player.team.get()

        # VALIDATIONS
        if not _validate_is_team_owner(self.response, player, team):
            return

        # DO SHIT
        team.ranked_start_hour = int(request_data['ranked_start_hour'])
        team.ranked_end_hour = int(request_data['ranked_end_hour'])
        team.put()

        set_json_response(self.response, {'code': "OK"})


def _validate_has_no_team(response, player):
    if player.team:
        error_400(response, "ERROR_HAS_TEAM", "Your player can only be part of 1 team.")
        return False
    else:
        return True


def _validate_is_team_owner(response, player, team):
    if not team.owner == player.key:
        error_400(response, "ERROR_NOT_OWNER", "Not the team owner.")
        return False
    else:
        return True


def _websocket_notify_team(team_key, event, value):
    for team_player in Player.query(Player.team == team_key).fetch():
        team_player.websocket_notify(event, value)

app = webapp2.WSGIApplication([
    (r'/api/teams/register', RegisterHandler),
    (r'/api/teams/rest/', TeamsHandler),
    (r'/api/teams/sendApplication', SendApplicationHandler),
    (r'/api/teams/acceptApplication', AcceptApplicationHandler),
    (r'/api/teams/declineApplication', DeclineApplicationHandler),
    (r'/api/teams/kickMember', KickMemberHandler),
    (r'/api/teams/updateConfig', UpdateConfigHandler)
], debug=True)
