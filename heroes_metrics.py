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

hero_metrics = [
    # MID
    {
        'name': 'Pudge',
        'potentials':  {
            'mid': 75,
            'offlane': 25,
            'support': 25,
            'carry': 0,
            'farm': 25,
            'gank': 100,
            'push': 25
        }
    },
    {
        'name': 'Anti-Mage',
        'potentials': {
            'mid': 25,
            'offlane': 50,
            'support': 0,
            'carry': 100,
            'farm': 100,
            'gank': 25,
            'push': 25
        }
    },
    {
        'name': 'Shadow Fiend',
        'potentials': {
            'mid': 75,
            'offlane': 0,
            'support': 0,
            'carry': 50,
            'farm': 100,
            'gank': 25,
            'push': 100
        }

    },
    {
        'name': 'Techies',
        'potentials': {
            'mid': 25,
            'offlane': 25,
            'support': 75,
            'carry': 0,
            'farm': 50,
            'gank': 25,
            'push': 100
        }
    },
    {
        'name': 'Tidehunter',
        'potentials': {
            'mid': 25,
            'offlane': 100,
            'support': 25,
            'carry': 25,
            'farm': 25,
            'gank': 75,
            'push': 25
        }

    },
    {
        'name': 'Clockwerk',
        'potentials': {
            'mid': 50,
            'offlane': 100,
            'support': 25,
            'carry': 0,
            'farm': 25,
            'gank': 100,
            'push': 25
        }

    },
    {
        'name': 'Tusk',
        'potentials': {
            'mid': 50,
            'offlane': 50,
            'support': 50,
            'carry': 25,
            'farm': 25,
            'gank': 100,
            'push': 50
        }
    },
    {
        'name': 'Crystal Maiden',
        'potentials': {
            'mid': 25,
            'offlane': 0,
            'support': 100,
            'carry': 0,
            'farm': 50,
            'gank': 75,
            'push': 25
        }

    },
    {
        'name': 'Lion',
        'potentials': {
            'mid': 50,
            'offlane': 0,
            'support': 100,
            'carry': 0,
            'farm': 25,
            'gank': 75,
            'push': 25
        }

    },
    {
        'name': 'Omniknight',
        'potentials': {
            'mid': 25,
            'offlane': 50,
            'support': 100,
            'carry': 25,
            'farm': 25,
            'gank': 25,
            'push': 25
        }
    },
]


def is_valid_hero_name(hero_name):
    for hero in hero_metrics:
        if hero['name'] == hero_name:
            return True
    return False


def get_flat_hero_name_list():
    names = []
    for hero in hero_metrics:
        names.append(hero['name'])
    return names