"""
Mid Potential: How well the hero does on this position.
Offlane potential: How well the hero does on this position.
Support potential: How good the hero is at supporting other heroes.
Carry potential: How effective gold is on this hero.
Farm potential: How effective the hero farms gold.
Gank potential: How good the hero is at ganking.
Push potential: How well the hero push given its abilities.


NOT IMPLEMENTED - BUT IDEAS FOR METRICS
Woods
Team fight
early game
mid game
late game

"""


heroes = {
    # MID
    'Pudge': {
        'potentials':  {
            'mid': 75,
            'off_lane': 25,
            'support': 25,
            'carry': 0,
            'farm': 25,
            'gank': 100,
            'push': 25
        }
    },
    'Anti-Mage': {
        'potentials': {
            'mid': 25,
            'off_lane': 50,
            'support': 0,
            'carry': 100,
            'farm': 100,
            'gank': 25,
            'push': 25
        }
    },
    'Shadow Fiend': {
        'potentials': {
            'mid': 75,
            'off_lane': 0,
            'support': 0,
            'carry': 50,
            'farm': 100,
            'gank': 25,
            'push': 100
        }

    },
    'Techies': {
        'potentials': {
            'mid': 25,
            'off_lane': 25,
            'support': 75,
            'carry': 0,
            'farm': 50,
            'gank': 25,
            'push': 100
        }
    },
    'Tidehunter': {
        'potentials': {
            'mid': 25,
            'off_lane': 100,
            'support': 25,
            'carry': 25,
            'farm': 25,
            'gank': 75,
            'push': 25
        }

    },
    'Clockwerk': {
        'potentials': {
            'mid': 50,
            'off_lane': 100,
            'support': 25,
            'carry': 0,
            'farm': 25,
            'gank': 100,
            'push': 25
        }

    },
    'Tusk': {
        'potentials': {
            'mid': 50,
            'off_lane': 50,
            'support': 50,
            'carry': 25,
            'farm': 25,
            'gank': 100,
            'push': 50
        }
    },
    'Crystal Maiden': {
        'potentials': {
            'mid': 25,
            'off_lane': 0,
            'support': 100,
            'carry': 0,
            'farm': 50,
            'gank': 75,
            'push': 25
        }

    },
    'Lion': {
        'potentials': {
            'mid': 50,
            'off_lane': 0,
            'support': 100,
            'carry': 0,
            'farm': 25,
            'gank': 75,
            'push': 25
        }

    },
    'Omniknight': {
        'potentials': {
            'mid': 25,
            'off_lane': 50,
            'support': 100,
            'carry': 25,
            'farm': 25,
            'gank': 25,
            'push': 25
        }
    },
}