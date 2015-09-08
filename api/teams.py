#!/usr/bin/env python

import webapp2
import logging
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

        ndb.get_context().clear_cache() # Required to get the new player as part of the get_data
        set_json_response(self.response, {'team': new_team.get_data('full'), 'player': player.get_data()})


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

        for team_player in Player.query(Player.team == team_key).fetch():
            team_player.websocket_notify('NewTeamApplication', team_application.get_data())

        set_json_response(self.response, {'code': "OK"})


class AcceptApplicationHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        application = TeamApplication.get_by_id(int(request_data['application_id']))
        application_to_team = application.team.get()

        # VALIDATIONS
        if not _validate_is_team_owner(self.response, player, application_to_team):
            return

        # DO SHIT
        applicant = application.player.get()
        applicant.team = application.team
        applicant.put()
        application.key.delete()

        set_json_response(self.response, {'code': "OK"})


class DeclineApplicationHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        application = TeamApplication.get_by_id(int(request_data['application_id']))
        application_to_team = application.team.get()

        # VALIDATIONS
        if not _validate_is_team_owner(self.response, player, application_to_team):
            return

        # DO SHIT
        application.key.delete()

        set_json_response(self.response, {'code': "OK"})


class KickMemberHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        kicked_player = Player.get_by_id(int(request_data['player_id']))
        kicked_player_team = kicked_player.team.get()

        # VALIDATIONS
        if not _validate_is_team_owner(self.response, player, kicked_player_team):
            return
        if player == kicked_player:
            error_400(self.response, "ERROR_CANT_KICK_SELF", "You cannot kick yourself from your own team. Are you retarded?")
            return

        # DO SHIT
        kicked_player.team = None
        kicked_player.put()

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


app = webapp2.WSGIApplication([
    (r'/api/teams/register', RegisterHandler),
    (r'/api/teams/rest/', TeamsHandler),
    (r'/api/teams/sendApplication', SendApplicationHandler),
    (r'/api/teams/acceptApplication', AcceptApplicationHandler),
    (r'/api/teams/declineApplication', DeclineApplicationHandler),
    (r'/api/teams/kickMember', KickMemberHandler),
], debug=True)
