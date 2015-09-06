from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from random import shuffle, randint
from gameconfig import EnergyConfig
import logging
from google.appengine.api import channel
import json
from datetime import datetime


class Player(ndb.Model):
    userid = ndb.StringProperty(required=True)
    nick = ndb.StringProperty(required=True)
    skill = ndb.IntegerProperty(required=True)
    team = ndb.KeyProperty(kind='Team')
    doing = ndb.KeyProperty(default=None)
    energy = ndb.IntegerProperty(default=EnergyConfig.maxEnergy)

    def get_data_nick_and_id(self):
        return {
            'id': self.key.id(),
            'nick': self.nick
        }

    def get_data(self, detail_level="simple"):
        data = {
            'id': self.key.id(),
            'nick': self.nick,
            'skill': int(self.skill / 1000.0),
            'team': self.team.get().get_data(detail_level) if self.team else None,
            'doing': self.doing.get().get_data() if self.doing else None,
            'energy': self.energy
        }

        if detail_level == "full":
            match_keys = [match_player.match for match_player in MatchPlayer.query(MatchPlayer.player == self.key).fetch()]
            matches_data = [match.get_data("simple") for match in ndb.get_multi(match_keys)]
            data.update({
                'matches': matches_data,
                'configs': [config.get_data() for config in PlayerConfig.query(PlayerConfig.player == self.key).fetch()]
            })

        return data

    def clear_doing(self):
        self.doing.delete()
        self.doing = None
        self.put()

    def websocket_notify(self, event, value):
        channel.send_message(self.userid, json.dumps({'event': event, 'value': value}))


class PlayerConfig(ndb.Model):
    player = ndb.KeyProperty(kind=Player)
    name = ndb.StringProperty(default="New config")
    active = ndb.BooleanProperty(default=False)

    def get_data(self):
        return {
            'id': self.key.id(),
            'name': self.name,
            'active': self.active,
        }


class Team(ndb.Model):
    name = ndb.StringProperty(required=True)
    owner = ndb.KeyProperty(kind=Player, required=True)

    def get_data(self, detail_level="simple"):
        data = {
            'id': self.key.id(),
            'name': self.name,
            'owner': self.owner.get().get_data_nick_and_id()
        }
        if detail_level == "full":
            data.update({
                'applications': [team_app.get_data() for team_app in TeamApplication.query(TeamApplication.team == self.key)],
                'members': [player.get_data_nick_and_id() for player in Player.query(Player.team == self.key)]
            })

        return data


class TeamApplication(ndb.Model):
    team = ndb.KeyProperty(kind=Team, required=True)
    player = ndb.KeyProperty(kind=Player, required=True)
    text = ndb.StringProperty(required=True)

    def get_data(self):
        return {
            'id': self.key.id(),
            'player': self.player.get().get_data_nick_and_id(),
            'text': self.text
        }


class MatchSoloQueue(ndb.Model):
    player = ndb.KeyProperty(kind=Player, required=True)
    type = ndb.StringProperty(required=True, choices=['Unranked', 'Ranked'])

    def get_data(self):
        return {
            'id': self.key.id(),
            'type': self.type,
            'what': '%sMatchSoloQueue' % self.type,
            'queued': MatchSoloQueue.query(MatchSoloQueue.type == self.type).count()
        }

    @classmethod
    def _pre_delete_hook(cls, key):
        match_queues = MatchSoloQueue.query(MatchSoloQueue.type == key.get().type)
        match_queues_after_deletion_count = match_queues.count() - 1
        for match_queue_left in match_queues:
            match_queue_left.player.get().websocket_notify("NewPlayerDoingQueueCount", match_queues_after_deletion_count)


class Match(ndb.Model):
    winning_faction = ndb.StringProperty(required=True, choices=['Dire', 'Radiant'])
    type = ndb.StringProperty(required=True, choices=['Bot', 'Unranked', 'Ranked'])
    date = ndb.DateTimeProperty(auto_now_add=True)

    def play_match(self, players):
        shuffle(players)
        alternated_faction_list = ['Dire', 'Radiant', 'Dire', 'Radiant', 'Dire', 'Radiant', 'Dire', 'Radiant', 'Dire', 'Radiant']
        self.cached_combatants = []
        for player in players:
            self.cached_combatants.append(MatchPlayer(
                player=player.key,
                faction=alternated_faction_list.pop(0)
            ))

        self._simulate_match()
        self._save_data()

    def play_bot_match(self, player):
        # Add player as combatant
        shuffled_factions_spots = self._get_shuffled_factions_spots()
        self.cached_combatants = []  # Cached so the data can be used without hitting db in get_data method
        self.cached_combatants.append(MatchPlayer(
            player=player.key,
            faction=shuffled_factions_spots.pop(0)
        ))

        # Generate bots
        for faction in self._get_shuffled_factions_spots():
            self.cached_combatants.append(MatchBot(
                nick="Lolbot",
                faction=faction
            ))

        self._simulate_match()
        self._save_data()

    def get_data(self, detail_level="simple"):
        data = {
            'id': self.key.id(),
            'winning_faction': self.winning_faction,
            'type': self.type,
            'date': self.date.strftime("%Y-%m-%d, %H:%M"),
            'date_epoch': int((self.date - datetime(1970, 1, 1)).total_seconds()),
        }

        if detail_level == "full":
            if hasattr(self, "cached_combatants"):
                match_combatants = self.cached_combatants
            else:
                match_combatants = MatchCombatant.query(MatchCombatant.match == self.key).fetch()
            data.update({
                'combatants': [match_combatant.get_data() for match_combatant in match_combatants]
            })

        return data

    def _simulate_match(self):
        self.winning_faction = 'Dire' if randint(0, 1) == 0 else 'Radiant'

    def _save_data(self):
        self.put()
        for combatant in self.cached_combatants:
            combatant.match = self.key
            combatant.put()

    def _get_shuffled_factions_spots(self):
        faction_spots = ['Dire', 'Dire', 'Dire', 'Dire', 'Dire', 'Radiant', 'Radiant', 'Radiant', 'Radiant', 'Radiant']
        shuffle(faction_spots)
        return faction_spots


class MatchCombatant(polymodel.PolyModel):
    match = ndb.KeyProperty(kind=Match, required=True)
    faction = ndb.StringProperty(required=True, choices=['Dire', 'Radiant'])

    def get_base_data(self):
        return {
            'id': self.key.id(),
            'faction': self.faction
        }


class MatchPlayer(MatchCombatant):
    player = ndb.KeyProperty(kind=Player, required=True)

    def get_data(self):
        data = self.get_base_data()
        data.update(self.player.get().get_data_nick_and_id())
        return data


class MatchBot(MatchCombatant):
    nick = ndb.StringProperty(required=True)

    def get_data(self):
        data = self.get_base_data()
        data.update({'nick': self.nick})
        return data
