#!/usr/bin/env python

import logging

import webapp2
from utils import *
from models import Player, PlayerConfig, OwnedEquipment
from metrics.heroes import is_valid_hero_name
from metrics.player_class import player_class_metrics, is_valid_player_class_name
from metrics.equipment import equipment_metrics, get_equipment_from_name


class RegisterHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        user = users.get_current_user()

        # VALIDATION
        if not validate_request_data(self.response, request_data, ['nick', 'player_class']):
            return
        if not validate_logged_inn(self.response):
            return
        if not self._validate_has_not_player_already(user):
            return
        if Player.query(Player.nick_lower == request_data['nick'].lower()).count() > 0:
            error_400(self.response, "ERROR_NICK_TAKEN", "The nickname %s is already taken" % request_data['nick'])
            return
        if not is_valid_player_class_name(request_data['player_class']):
            error_400(self.response, "ERROR_BAD_PLAYER_CLASS", "Player class ' %s ' is not valid." % request_data['player_class'])
            return

        # REGISTER PLAYER
        new_player = Player(
            id=user.user_id(),
            nick=request_data['nick']
        )

        for player_class in player_class_metrics:
            if player_class['name'] == request_data['player_class']:
                logging.info(player_class['stat_modifiers'])
                for stat_name, stat_value in player_class['stat_modifiers'].iteritems():
                    current_stat_value = getattr(new_player, stat_name)
                    new_stat_value = current_stat_value + stat_value
                    setattr(new_player, stat_name, new_stat_value)

        new_player.put().get()
        set_json_response(self.response, new_player.get_data("full"))

    def _validate_has_not_player_already(self, user):
        player_key = ndb.Key(Player, user.user_id())
        if Player.query(Player.key == player_key).count() > 0:
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
        player = current_user_player()

        if player:
            set_json_response(self.response, {'has_player': True, 'player': player.get_data('full')})
        else:
            register_player_form_data = {'player_classes': player_class_metrics}
            set_json_response(self.response, {'has_player': False, 'register_player_form_data': register_player_form_data})


class StopDoingHandler(webapp2.RequestHandler):
    def post(self):
        player = current_user_player()

        stop_doing_result = player.stop_doing()
        if stop_doing_result:
            error_400(self.response, "ERROR_CANT_STOP_DOING", stop_doing_result)
            return

        set_json_response(self.response, {'code': "OK"})


class AddConfigHandler(webapp2.RequestHandler):
    def post(self):
        player = current_user_player()
        first_config = PlayerConfig.query(PlayerConfig.player == player.key).count() == 0
        new_config = PlayerConfig(player=player.key, active=first_config).put().get()
        set_json_response(self.response, new_config.get_data())


class UpdateConfigHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        config = PlayerConfig.get_by_id(int(request_data['id']))
        updated_hero_priorities = self._hero_priorities_cleaned_for_empty(request_data['hero_priorities'])

        # VALIDATION
        if not config.player == player.key:
            error_400(self.response, "ERROR_NOT_YOUR_PLAYER", "You cant update another players config. You api-hacking or what?")
            return
        if not self._validate_hero_priorities(updated_hero_priorities):
            return

        # UPDATE
        config.name = request_data['name']
        config.hero_priorities = updated_hero_priorities
        config.troll_level = request_data['troll_level']
        config.flame_level = request_data['flame_level']
        config.put()

        set_json_response(self.response, {'code': "OK"})

    @staticmethod
    def _hero_priorities_cleaned_for_empty(hero_priorities):
        return [h for h in hero_priorities if (h["name"] or h["role"])]

    def _validate_hero_priorities(self, hero_priorities):
        for hero_priority in hero_priorities:
            # VALIDATE HERO NAMES
            if not is_valid_hero_name(hero_priority['name']):
                error_400(self.response, "ERROR_BAD_HERO_NAME", "Hero name ' %s ' is not valid." % hero_priority['name'])
                return False
            # VALIDATE ROLES
            if hero_priority['role'] not in ["mid", "support", "carry", "offlane"]:
                error_400(self.response, "ERROR_BAD_ROLE", "Role ' %s ' is not valid." % hero_priority['role'])
                return False
        return True


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
            error_400(self.response, "ERROR_NOT_YOUR_PLAYER", "You activate another players config. You api-hacking or what?")
            return

        # UPDATE
        for active_config in PlayerConfig.query(PlayerConfig.player == player.key, PlayerConfig.active == True).fetch():
            active_config.active = False
            active_config.put()

        config.active = True
        config.put()

        set_json_response(self.response, {'code': "OK"})


class ShopEquipmentListHandler(webapp2.RequestHandler):
    def get(self):
        set_json_response(self.response, equipment_metrics)


class BuyEquipmentHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        equipment_to_buy = get_equipment_from_name(request_data['equipment_name'])

        # VALIDATION
        if OwnedEquipment.query(OwnedEquipment.player == player.key, OwnedEquipment.name == equipment_to_buy['name']).count() > 0:
            error_400(self.response, "ERROR_HAVE_EQUIPMENT", "You already have the item '%s'." % equipment_to_buy['name'])
            return
        if equipment_to_buy['cost'] > player.cash:
            error_400(self.response, "ERROR_NOT_ENOUGH_CASH", "Cant afford item. You have %s, the cost is %s" % (player.cash, equipment_to_buy['cost']))
            return

        # BUY
        new_equipment = OwnedEquipment(
            player=player.key,
            name=equipment_to_buy['name'],
            type=equipment_to_buy['type']
        ).put().get()

        player.cash -= equipment_to_buy['cost']
        player.put()

        set_json_response(self.response, new_equipment.get_data())


class SetEquippedStateHandler(webapp2.RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logging.info(request_data)
        player = current_user_player()
        equipment = get_equipment_from_name(request_data['equipment_name'])

        owned_equipment = OwnedEquipment.query(OwnedEquipment.player == player.key, OwnedEquipment.name == equipment['name']).get()

        # VALIDATE
        if not validate_request_data(self.response, request_data, ['value']):
            return
        if not owned_equipment:
            error_400(self.response, "ERROR_EQUIPMENT_NOT_FOUND", "Does not seem like you own this equipment '%s'" % equipment['name'])
            return

        if request_data['value']:
            has_equipped_of_type = OwnedEquipment.query(OwnedEquipment.player == player.key, OwnedEquipment.type == equipment['type'], OwnedEquipment.is_equipped == True).count() > 0
            if has_equipped_of_type:
                error_400(self.response, "ERROR_EQUIPPED_OF_TYPE", "You already equipped an equipment of type '%s'" % equipment['type'])
                return
            else:
                owned_equipment.is_equipped = True
        else:
            owned_equipment.is_equipped = False

        owned_equipment.put()

        set_json_response(self.response, {'code': "OK"})


app = webapp2.WSGIApplication([
    (r'/api/players/register', RegisterHandler),
    (r'/api/players/my', MyHandler),
    (r'/api/players/stopDoing', StopDoingHandler),
    (r'/api/players/addConfig', AddConfigHandler),
    (r'/api/players/updateConfig', UpdateConfigHandler),
    (r'/api/players/deleteConfig', DeleteConfigHandler),
    (r'/api/players/setActiveConfig', SetActiveConfigHandler),
    (r'/api/players/shopEquipmentList', ShopEquipmentListHandler),
    (r'/api/players/buyEquipment', BuyEquipmentHandler),
    (r'/api/players/setEquippedState', SetEquippedStateHandler),
], debug=True)
