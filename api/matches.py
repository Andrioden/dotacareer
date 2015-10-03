#!/usr/bin/env python

import logging
from google.appengine.ext import ndb
import webapp2
from utils import *
from models import MatchSoloQueue, Match, MatchPlayer, Bet


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
            websocket_notify_player("Match_NewQueueCount", match_queue.player, "player.doing", {'queued': all_match_queues_count})


class PlayAgainstBotsHandler(webapp2.RequestHandler):
    def post(self):
        player = current_user_player()

        if player.doing:
            error_400(self.response, "ERROR_PLAYER_BUSY", "Player is busy.")
            return

        bot_match = Match(type="Bot")
        bot_match.setup_bot_match(player)

        player.doing = bot_match.key
        player.put()

        set_json_response(self.response, bot_match.get_data("full"))


class BetHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()

        match_key = ndb.Key(Match, int(request_data['match_id']))
        match = match_key.get()
        match_player = MatchPlayer.query(MatchPlayer.match == match_key, MatchPlayer.player == player.key).get()

        if match.state() == "finished":
            error_400(self.response, "ERROR_FINISHED_GAME", "You can not bet on a finished game.")
            return
        if not validate_request_data(self.response, request_data, ['match_id', 'bet']):
            return
        if not match_player:
            error_400(self.response, "ERROR_NOT_OWN_GAME", "You have to bet on your own game.")
            return

        if request_data['bet']['id']:
            bet = Bet.get_by_id(int(request_data['bet']['id']))
        else:
            bet = Bet(match=match_key, player=player.key, winning_faction=match_player.faction)

        new_bet_value = int(request_data['bet']['value'])
        bet_value_dif = new_bet_value - bet.value
        if bet_value_dif < 0:
            error_400(self.response, "ERROR_BET_LOWER", "Your new bet %s is lower than your previous bet %s" % (new_bet_value, bet.value))
            return
        if bet_value_dif > player.cash:
            error_400(self.response, "ERROR_NOT_ENOUGH_CASH", "Not enough cash. Your player has %s cash and your new bet requires %s" % (player.cash, bet_value_dif))
            return

        bet.value = new_bet_value
        bet.put()

        player.cash -= bet_value_dif
        player.put()

        client_object_path = "player.matches.[%s].bets.[%s]" % (match_key.id(), bet.key.id())
        match.websocket_notify_players("Match_UpdatedOrNewBet", client_object_path, bet.get_data(), player.key)
        set_json_response(self.response, {'bet': bet.get_data(), 'cash': player.cash})


class RESTHandler(webapp2.RequestHandler):
    def get(self, match_id):
        match = Match.get_by_id(int(match_id))
        set_json_response(self.response, match.get_data('full'))


app = webapp2.WSGIApplication([
    (r'/api/matches/playAgainstBots', PlayAgainstBotsHandler),
    (r'/api/matches/joinSoloQueue', JoinSoloQueueHandler),
    (r'/api/matches/bet', BetHandler),
    (r'/api/matches/rest/(\d+)', RESTHandler),
], debug=True)