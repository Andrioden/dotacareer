
equipment_metrics = [
    {
        'name': "Mouse",
        'type': "mouse",
        'cost': 20,
        'stat_modifiers': {
            'stat_skill': 5
        }
    },
    {
        'name': "MouseMan",
        'type': "mouse",
        'cost': 200,
        'stat_modifiers': {
            'stat_skill': 7
        }
    },
    {
        'name': "Diamondback",
        'type': "mouse",
        'cost': 2000,
        'stat_modifiers': {
            'stat_skill': 13
        }
    },
    {
        'name': "Deathadder",
        'type': "mouse",
        'cost': 20000,
        'stat_modifiers': {
            'stat_skill': 14
        }
    }
]


def get_flat_equipment_name_list(type=None):
    names = []
    for equipment in equipment_metrics:
        if type is None or type == equipment['type']:
            names.append(equipment['name'])
    return names
