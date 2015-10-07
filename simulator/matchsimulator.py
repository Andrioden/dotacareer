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
        self._log("--- Match phase ---")
        self._log("Running simulator of dire (%s players) vs radiant (%s players)" % (len(self.dire), len(self.radiant)))
        self.winning_faction = 'Dire' if random.randint(0, 1) == 0 else 'Radiant'
        self._set_stat_outcomes()

    def get_printable_log(self):
        return '\n'.join(self.logs)

    def _set_stat_outcomes(self):
        for sim_player in (self.dire + self.radiant):
            if sim_player.db_player:
                # Skill
                outcome = random.uniform(-0.2, 1.0)
                self.logs.append("%s stat outcome for '%s': %s" % (sim_player.name, "stat_skill", outcome))
                sim_player.stat_outcomes.append(StatOutcome("stat_skill", outcome))

                # Hero overall
                outcome = random.uniform(-0.2, 1.0)
                self.logs.append("%s stat outcome for %s.%s: %s" % (sim_player.name, sim_player.hero, "stat_overall", outcome))
                sim_player.stat_outcomes.append(StatOutcome("stat_overall", outcome, True, sim_player.hero))

    def _log(self, msg):
        print msg
        self.logs.append(msg)


class MatchSimulatorPlayer:
    """
    :type stat_outcomes: list[StatOutcome]
    """
    def __init__(self, name, hero, skill, db_combatant=None, db_player=None):
        self.name = name
        self.hero = hero
        self.skill = skill
        self.stat_outcomes = []
        self.db_combatant = db_combatant
        self.db_player = db_player


class StatOutcome:

    def __init__(self, stat, outcome, is_hero_stat=False, hero=None):
        self.stat = stat
        self.outcome = outcome
        self.is_hero_stat = is_hero_stat
        self.hero = hero

    # def to_dict(self):
    #     return {
    #         'stat': self.stat,
    #         'outcome': self.outcome,
    #         'is_hero_stat': self.is_hero_stat,
    #         'hero': self.hero
    #     }