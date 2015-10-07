from matchsimulator import MatchSimulator, MatchSimulatorPlayer

DEFAULT_BOT_SKILL = 5


class MatchSimulatorFactory:

    def __init__(self):
        pass

    @staticmethod
    def create(combatants):
        """
        "rtype": MatchSimulator
        """

        dire = []
        radiant = []
        for combatant in combatants:
            if type(combatant).__name__ == "MatchBot":
                sim_player = MatchSimulatorPlayer(combatant.nick, combatant.hero, DEFAULT_BOT_SKILL, None, None)
            else:
                player = combatant.player.get()
                sim_player = MatchSimulatorPlayer(player.nick, combatant.hero, player.stat_skill, combatant, player)

            if combatant.faction == "Dire":
                dire.append(sim_player)
            else:
                radiant.append(sim_player)

        return MatchSimulator(dire, radiant)
