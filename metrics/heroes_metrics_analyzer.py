from heroes import hero_metrics
import json
import operator

def print_sorted_pretty(list):
    for list_item in sorted(list):
        print list_item


if __name__ == '__main__':
    heroes_potentials = []
    for hero in hero_metrics:
        potentials_sum = sum(hero['potentials'].values())
        heroes_potentials.append([potentials_sum, hero['name']])
    print_sorted_pretty(heroes_potentials)