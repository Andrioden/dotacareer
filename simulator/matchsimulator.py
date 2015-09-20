import random
from google.appengine.ext import ndb
import models


class MatchSimulator:

    def __init__(self, dire, radiant):
        """
        :type dire: list[MatchSimulatorPlayer]
        :type radiant: list[MatchSimulatorPlayer]
        :return:
        """
        self.dire = dire
        self.radiant = radiant
        self.winning_faction = None
        self.logs = []

    def run(self):
        self._log("Running simulator of dire (%s players) vs radiant (%s players)" % (len(self.dire), len(self.radiant)))
        self.winning_faction = 'Dire' if random.randint(0, 1) == 0 else 'Radiant'
        self._set_stat_outcomes()

    def get_printable_log(self):
        return '\n'.join(self.logs)

    def _set_stat_outcomes(self):
        for sim_player in (self.dire + self.radiant):
            if sim_player.db_player:
                outcome = random.uniform(-1.0, 1.0)
                self.logs.append("%s stat outcome for '%s': %s" % (sim_player.name, "skill", outcome))
                sim_player.add_stat_outcome("skill", outcome)

    def _log(self, msg):
        print msg
        self.logs.append(msg)


class MatchSimulatorPlayer:

    def __init__(self, name, hero, skill, db_combatant=None, db_player=None):
        self.name = name
        self.hero = hero
        self.skill = skill
        self.stat_outcomes = []
        self.db_combatant = db_combatant
        self.db_player = db_player

    def add_stat_outcome(self, stat, outcome):
        self.stat_outcomes.append({
            'stat': stat,
            'outcome': outcome
        })
