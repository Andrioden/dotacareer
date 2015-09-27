"""
stat_:

"""

player_class_metrics = [
    {
        'name': 'Flamer',
        'description': 'This player has a tendency to flame his opponents, but this also increases his chance of flaming his own teammates. More resistant to flame and trolling than others.',
        'stat_modifiers':  {
            'stat_flaming': 10.0,
            'stat_resistance_flaming': 3.0,
            'stat_resistance_trolling': 3.0
        }
    },
    {
        'name': 'Arrogant SOB',
        'description': 'Always considers himself the center of the team. Is confident and has quick decision time. Plays best as carry and mid but hates the other roles.',
        'stat_modifiers': {
            'stat_confidence': 10.0,
            'stat_mid': 6.0,
            'stat_carry': 6.0,
            'stat_gank': -3.0,
            'stat_push': -3.0,
            'stat_support': -3.0,
            'stat_offlane': -3.0
        }
    }
]


def is_valid_player_class_name(player_class_name):
    for player_class in player_class_metrics:
        if player_class['name'] == player_class_name:
            return True
    return False

"""
def get_flat_player_class_name_list():
    names = []
    for player_class in player_class_metrics:
        names.append(player_class['name'])
    return names
"""