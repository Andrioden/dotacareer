from heroes import heroes
import json
import operator

def print_sorted_pretty(list):
    for list_item in sorted(list):
        print list_item


if __name__ == '__main__':
    heroes_potentials = []
    for hero_name, config in heroes.iteritems():
        potentials_sum = sum(config['potentials'].values())
        heroes_potentials.append([potentials_sum, hero_name])
    print_sorted_pretty(heroes_potentials)