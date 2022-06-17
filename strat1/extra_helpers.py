import math
from datetime import datetime


from kaggle_environments.envs.kore_fleets.helpers import ShipyardAction
# from random import choice, randint, randrange, sample, seed, random


# ref @egrehbbt
def max_flight_plan_len_for_ship_count(ship_count):
    return math.floor(2 * math.log(ship_count)) + 1


# ref @egrehbbt
def min_ship_count_for_flight_plan_len(flight_plan_len):
    return math.ceil(math.exp((flight_plan_len - 1) / 2))


# ref @egrehbbt
def collection_rate_for_ship_count(ship_count):
    return min(math.log(ship_count) / 20, 0.99)


def get_total_ships(board, player):
    ships = 0
    for fleet in board.fleets.values():
        if fleet.player_id == player:
            ships += fleet.ship_count
    for shipyard in board.shipyards.values():
        if shipyard.player_id == player:
            ships += shipyard.ship_count
    return ships


def spawn_ships(shipyard, remaining_kore, spawn_cost):
    return ShipyardAction.spawn_ships(min(shipyard.max_spawn, int(remaining_kore/spawn_cost)))


def add_log(msg, log_file="kore_logs.txt"):
    # Open a file with access mode 'a'
    with open(log_file, "a") as file_object:
        file_object.write(str(datetime.now().time()) + ": " + msg + "\n")
