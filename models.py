from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
import random
from gameconfig import EnergyConfig, CashConfig, BettingConfig
import logging, json, random, copy
from google.appengine.api import channel
import datetime
from heroes_metrics import get_flat_hero_name_list, hero_metrics
from simulator.factories import MatchSimulatorFactory
from simulator.matchsimulator import MatchSimulator # Imported so autocomplete works


class Player(ndb.Model):
    userid = ndb.StringProperty(required=True)
    nick = ndb.StringProperty(required=True)
    nick_lower = ndb.ComputedProperty(lambda self: self.nick.lower())
    skill = ndb.FloatProperty(required=True)
    team = ndb.KeyProperty(kind='Team')
    doing = ndb.KeyProperty(default=None)
    energy = ndb.IntegerProperty(default=EnergyConfig.maxEnergy)
    cash = ndb.FloatProperty(default=CashConfig.startingCash)

    def get_data_nick_and_id(self):
        return {
            'id': self.key.id(),
            'nick': self.nick
        }

    def get_data(self, detail_level="simple"):
        data = {
            'id': self.key.id(),
            'nick': self.nick,
            'skill': int(self.skill),
            'team': self.team.get().get_data(detail_level) if self.team else None,
            'doing': self.doing.get().get_data() if self.doing else None,
            'energy': self.energy,
            'cash': self.cash
        }

        if detail_level == "full":
            match_keys = [match_player.match for match_player in MatchPlayer.query(MatchPlayer.player == self.key).fetch()]
            matches_data = [match.get_data("simple") for match in ndb.get_multi(match_keys)]
            data.update({
                'matches': matches_data,
                'configs': [config.get_data() for config in PlayerConfig.query(PlayerConfig.player == self.key).fetch()]
            })

        return data

    def get_active_player_config(self):
        return PlayerConfig.query(PlayerConfig.player == self.key, PlayerConfig.active == True).get()

    def stop_doing(self):
        doing = self.doing.get()
        if "MatchSoloQueue" in doing.what():
            self.doing.delete()
            self.doing = None
            self.put()
            return True
        else:
            return "Cant stop doing %s" % doing.what()

    def websocket_notify(self, event, value):
        channel.send_message(self.userid, json.dumps({'event': event, 'value': value}))


class PlayerConfig(ndb.Model):
    player = ndb.KeyProperty(kind=Player)
    name = ndb.StringProperty(default="New config")
    active = ndb.BooleanProperty(default=False)
    """
    Hero priorities is a ordered list with dicts in the following format:
    {
        'role': string,
        'name': string
    }
    """
    hero_priorities = ndb.JsonProperty()

    def get_data(self):
        return {
            'id': self.key.id(),
            'name': self.name,
            'active': self.active,
            'hero_priorities': self.hero_priorities if self.hero_priorities else []
        }


class Team(ndb.Model):
    name = ndb.StringProperty(required=True)
    owner = ndb.KeyProperty(kind=Player, required=True)
    ranked_last_match = ndb.DateTimeProperty(default=datetime.datetime.now())
    ranked_start_hour = ndb.IntegerProperty() # Is influenced by local time, so its not 0-24, it can be negative number
    ranked_end_hour = ndb.IntegerProperty() # Is influenced by local time, so its not 0-24, it can be negative number

    def get_data(self, detail_level="simple"):
        data = {
            'id': self.key.id(),
            'name': self.name,
            'owner': self.owner.get().get_data_nick_and_id()
        }
        if detail_level == "full":
            data.update({
                'ranked_time': {
                    'start_hour': self.ranked_start_hour,
                    'end_hour': self.ranked_end_hour,
                },
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

    def what(self):
        """
        Doing information. Code will be written like this. player.doing.what
        """
        return '%sMatchSoloQueue' % self.type

    def get_data(self):
        return {
            'id': self.key.id(),
            'type': self.type,
            'what': self.what(),
            'queued': MatchSoloQueue.query(MatchSoloQueue.type == self.type).count()
        }

    @classmethod
    def _pre_delete_hook(cls, key):
        match_queues = MatchSoloQueue.query(MatchSoloQueue.type == key.get().type)
        match_queues_after_deletion_count = match_queues.count() - 1
        for match_queue_left in match_queues:
            match_queue_left.player.get().websocket_notify("NewPlayerDoingQueueCount", match_queues_after_deletion_count)


class Match(polymodel.PolyModel):
    type = ndb.StringProperty(required=True, choices=['Bot', 'Unranked', 'Ranked', 'TeamRanked'])
    date = ndb.DateTimeProperty(required=True)
    winning_faction = ndb.StringProperty(choices=['Dire', 'Radiant'])
    logs = ndb.StringProperty(repeated=True)

    def state(self):
        if self.winning_faction:
            return "finished"
        else:
            return "bettable"

    def what(self):
        """
        Doing information. Code will be written like this. player.doing.what
        """
        return "%sMatch" % self.type

    def get_data(self, detail_level="simple"):
        data = {
            'id': self.key.id(),
            'winning_faction': self.winning_faction,
            'type': self.type,
            'what': self.what(),
            'date_epoch': int((self.date - datetime.datetime(1970, 1, 1)).total_seconds()),
            'state': self.state()
        }

        if detail_level == "full":
            if hasattr(self, "cached_combatants"):
                match_combatants = self.cached_combatants
            else:
                match_combatants = MatchCombatant.query(MatchCombatant.match == self.key).fetch()
            data.update({
                'combatants': [match_combatant.get_data() for match_combatant in match_combatants],
                'bets': [bet.get_data() for bet in Bet.query(Bet.match == self.key)],
                'logs': self.logs
            })

        return data

    def setup_soloqueue_match(self, players):
        self.date = datetime.datetime.now() + datetime.timedelta(minutes=BettingConfig.betting_window_minutes)
        random.shuffle(players)
        alternated_faction_list = ['Dire', 'Radiant', 'Dire', 'Radiant', 'Dire', 'Radiant', 'Dire', 'Radiant', 'Dire', 'Radiant']
        hero_name_pool = [hero['name'] for hero in hero_metrics]
        random.shuffle(hero_name_pool)
        self.cached_combatants = []
        for player in players:
            self.cached_combatants.append(MatchPlayer(
                player=player.key,
                faction=alternated_faction_list.pop(0),
                hero=self._pop_prioritized_hero(player, hero_name_pool)
            ))

        self.put()
        self._put_combatants()

    def setup_bot_match(self, player):
        self.date = datetime.datetime.now() + datetime.timedelta(minutes=BettingConfig.betting_window_minutes)
        # Add player as combatant
        hero_name_pool = [hero['name'] for hero in hero_metrics]
        random.shuffle(hero_name_pool)

        shuffled_factions_spots = self._get_shuffled_factions_spots()
        self.cached_combatants = []  # Cached so the data can be used without hitting db in get_data method
        self.cached_combatants.append(MatchPlayer(
            player=player.key,
            faction=shuffled_factions_spots.pop(0),
            hero=self._pop_prioritized_hero(player, hero_name_pool)
        ))

        # Generate bots
        random.shuffle(hero_name_pool)
        for faction in shuffled_factions_spots:
            self.cached_combatants.append(MatchBot(
                nick="Lolbot",
                faction=faction,
                hero=hero_name_pool.pop()
            ))

        self.put()
        self._put_combatants()

    def play_match(self):
        simulator = MatchSimulatorFactory().create(MatchCombatant.query(MatchCombatant.match == self.key).fetch())
        simulator.run()
        logging.info(simulator.get_printable_log())

        self.winning_faction = simulator.winning_faction
        self.logs.extend(simulator.logs)

        for sim_player in (simulator.dire + simulator.radiant):
            if sim_player.db_combatant:
                sim_player.db_combatant.stat_outcomes = sim_player.stat_outcomes
                for stat_outcome in sim_player.stat_outcomes:
                    current_stat_value = getattr(sim_player.db_player, stat_outcome['stat'])
                    new_stat_value = current_stat_value + stat_outcome['outcome']
                    setattr(sim_player.db_player, stat_outcome['stat'], new_stat_value)
                sim_player.db_combatant.put()
                sim_player.db_player.put()

        self.put()
        self._payout_bets()

    def _pop_prioritized_hero(self, player, hero_name_pool):
        active_player_config = PlayerConfig.query(PlayerConfig.player == player.key, PlayerConfig.active == True).get()
        if active_player_config and active_player_config.hero_priorities:
            for hero_pri in active_player_config.hero_priorities:
                for hero_name in hero_name_pool:
                    if hero_pri['name'] == hero_name:
                        hero_name_pool.remove(hero_name)
                        return hero_name
        # No prioritized hero available, pick a random
        return hero_name_pool.pop()

    def _payout_bets(self):
        for bet in Bet.query(Bet.match == self.key):
            if bet.winning_faction == self.winning_faction:
                player = bet.player.get()
                payout = bet.value * 2
                player.cash += payout
                player.put()
                bet.payout = payout
                player.websocket_notify("CashChange", payout)
            else:
                bet.payout = 0
            bet.put()

    def _put_combatants(self):
        for combatant in self.cached_combatants:
            combatant.match = self.key
            combatant.put()

    def _get_shuffled_factions_spots(self):
        faction_spots = ['Dire', 'Dire', 'Dire', 'Dire', 'Dire', 'Radiant', 'Radiant', 'Radiant', 'Radiant', 'Radiant']
        random.shuffle(faction_spots)
        return faction_spots


class TeamMatch(Match):
    dire = ndb.KeyProperty(kind=Team, required=True)
    radiant = ndb.KeyProperty(kind=Team, required=True)

    def setup_team_match(self, teams):
        self.date = datetime.datetime.now() + datetime.timedelta(minutes=BettingConfig.betting_window_minutes)

        random.shuffle(teams)
        dire = teams.pop()
        radiant = teams.pop()

        dire_players = Player.query(Player.team == dire.key, Player.doing == None).fetch()
        radiant_players = Player.query(Player.team == radiant.key, Player.doing == None).fetch()

        if len(dire_players) == 0 or len(radiant_players) == 0:
            raise Exception("0 dire or radiant players, this should rarely happen. Well, maybe. dire: %s radiant: %s" % (len(dire_players), len(radiant_players)))

        self.logs.append("--- Picking phase ---")
        if random.randint(0,1) == 1:
            picking_order = ["Dire", "Radiant", "Radiant", "Dire", "Radiant", "Dire", "Radiant", "Dire", "Radiant", "Dire"]
            self.logs.append("Dire won coin flip and picks first")
        else:
            picking_order = ["Radiant", "Dire", "Dire", "Radiant", "Dire", "Radiant", "Dire", "Radiant", "Dire", "Radiant"]
            self.logs.append("Dire won coin flip and picks first")

        hero_name_pool = [hero['name'] for hero in hero_metrics]
        random.shuffle(hero_name_pool)
        players = []
        self.cached_combatants = []
        for faction in picking_order:
            picking_faction_player_list = dire_players if faction == "Dire" else radiant_players
            if len(picking_faction_player_list) == 0:
                continue
            player = picking_faction_player_list.pop()

            players.append(player)

            picked_hero = self._pop_prioritized_hero(player, hero_name_pool)
            self.logs.append("%s picked %s for %s" % (faction, picked_hero, player.nick))
            self.cached_combatants.append(MatchPlayer(
                player=player.key,
                faction=faction,
                hero=picked_hero
            ))

        # SAVE
        dire.ranked_last_match = datetime.datetime.now()
        dire.put()
        radiant.ranked_last_match = datetime.datetime.now()
        radiant.put()
        self.dire = dire.key
        self.radiant = radiant.key
        self.put()
        self._put_combatants()
        return players


class MatchCombatant(polymodel.PolyModel):
    match = ndb.KeyProperty(kind=Match, required=True)
    faction = ndb.StringProperty(required=True, choices=['Dire', 'Radiant'])
    hero = ndb.StringProperty(required=True, choices=get_flat_hero_name_list())
    """
    stat_outcomes is a list in the following format:
    {
        'stat' string, # the variable name on the player/playerstat object
        'outcome: float, # the outcome/change of the stat value
    }
    """
    stat_outcomes = ndb.JsonProperty()

    def get_base_data(self):
        return {
            'id': self.key.id(),
            'faction': self.faction,
            'hero': self.hero,
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


class Bet(ndb.Model):
    match = ndb.KeyProperty(kind=Match, required=True)
    player = ndb.KeyProperty(kind=Player, required=True)
    value = ndb.IntegerProperty(default=0)
    winning_faction = ndb.StringProperty(required=True, choices=['Dire', 'Radiant'])
    payout = ndb.IntegerProperty()

    def get_data(self):
        return {
            'id': self.key.id(),
            'player': self.player.get().get_data_nick_and_id(),
            'value': self.value,
            'winning_faction': self.winning_faction,
            'payout': self.payout
        }