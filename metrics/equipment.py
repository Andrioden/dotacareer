
equipment_metrics = [

    # MOUSE

    {
        'name': "Mouse",
        'type': "mouse",
        'cost': 20,
        'stat_modifiers': {
            'stat_skill': 2
        },
        'cheapest_of_type': True  # GUI Helper variable
    },
    {
        'name': "MouseMan",
        'type': "mouse",
        'cost': 200,
        'stat_modifiers': {
            'stat_skill': 3
        }
    },
    {
        'name': "Diamondback",
        'type': "mouse",
        'cost': 2000,
        'stat_modifiers': {
            'stat_skill': 5
        }
    },
    {
        'name': "Deathadder",
        'type': "mouse",
        'cost': 20000,
        'stat_modifiers': {
            'stat_skill': 6
        }
    },

    # KEYBOARD

    {
        'name': "Keyboard",
        'type': "keyboard",
        'cost': 5,
        'stat_modifiers': {
            'stat_skill': 2,
            'stat_flaming': 1,
            'stat_trolling': 1
        },
        'cheapest_of_type': True  # GUI Helper variable
    },
    {
        'name': "Lolitech",
        'type': "keyboard",
        'cost': 500,
        'stat_modifiers': {
            'stat_skill': 3,
            'stat_flaming': 1,
            'stat_trolling': 1
        }
    },
]


def get_flat_equipment_name_list(type=None):
    names = []
    for equipment in equipment_metrics:
        if type is None or type == equipment['type']:
            names.append(equipment['name'])
    return names


def get_equipment_from_name(name):
    for equipment in equipment_metrics:
        if equipment['name'] == name:
            return equipment