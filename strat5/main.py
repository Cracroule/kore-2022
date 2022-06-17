import math
from random import choice, randint, randrange, sample, seed, random

from kaggle_environments.envs.kore_fleets.kore_fleets import get_closest_enemy_shipyard, Point, Direction, \
    ShipyardAction, Board, get_shortest_flight_path_between
# from kaggle_environments.envs.kore_fleets.helpers import *
# from kaggle_environments.envs.kore_fleets.kore_fleets import Point


def start_sequence(me, shipyard, turn):
    feel_shift = 0  # and pickup turn19 B9 or 1 and 17 opposite dir
    if turn == 2:
        next_action = ShipyardAction.launch_fleet_with_flight_plan(2, "E")
    elif turn == 4:
        next_action = ShipyardAction.launch_fleet_with_flight_plan(2, "W")
    elif turn == 7:
        next_action = ShipyardAction.launch_fleet_with_flight_plan(3, "N" + str(feel_shift + 3) + "E")
    elif turn == 9:
        next_action = ShipyardAction.launch_fleet_with_flight_plan(3, "N" + str(feel_shift + 2) + "E")
    elif turn == 11:
        next_action = ShipyardAction.launch_fleet_with_flight_plan(3, "N" + str(feel_shift + 1) + "E")
    elif turn == 13:
        next_action = ShipyardAction.launch_fleet_with_flight_plan(3, "N" + str(feel_shift) + "E")
    elif turn == 16:
        # shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(shipyard.ship_count, "S")
        next_action = ShipyardAction.launch_fleet_with_flight_plan(shipyard.ship_count, "N9S")
        # shipyard.next_action = spawn_ships(shipyard, remaining_kore, spawn_cost)
    else:
        next_action = ShipyardAction.spawn_ships(min(shipyard.max_spawn, int(me.kore / 10)))
    # shipyard.next_action = next_action
    # if turn < 25:
    #     print(turn, shipyard.position, shipyard.ship_count, shipyard.max_spawn, "-->", shipyard.next_action)
    return next_action


# create another shipyard
def expand(shipyard):
    # TODO: actual implementation
    flight_plan = "N2EC"
    sent_ships = shipyard.ship_count
    return ShipyardAction.launch_fleet_with_flight_plan(sent_ships, flight_plan)


def nb_ships_to_send(available_ships):
    if available_ships < 2:
        return 0
    if available_ships == 2:
        return 2
    if available_ships < 5:
        return 3
    if available_ships < 8:
        return 5
    if available_ships < 13:
        return 8
    if available_ships < 21:
        return 13
    if available_ships < 34:
        return 21
    if available_ships < 55:
        return 34
    return 55


def mine(shipyard):
    # TODO: actual implementation
    nb_mining_ships = nb_ships_to_send(shipyard.ship_count)
    if nb_mining_ships == 2:
        flight_plan = "NS"
    else:
        flight_plan = "N4S"
    return ShipyardAction.launch_fleet_with_flight_plan(nb_mining_ships, flight_plan)


def agent(obs, config):

    board = Board(obs, config)
    me = board.current_player
    remaining_kore = me.kore
    shipyards = me.shipyards
    convert_cost = board.configuration.convert_cost
    size = board.configuration.size
    spawn_cost = board.configuration.spawn_cost
    turn = board.step

    invading_fleet_size = 75
    convert_cost_buffer = 80
    mining_search_radius = 10
    defence_radius = 7

    # opponent_shipyards = board.opponents[0].shipyards[0].position

    shipyards = sample(shipyards, len(shipyards))
    for shipyard in shipyards:
        if turn < 18:
            next_action = start_sequence(me, shipyard, turn)
        elif shipyard.ship_count > 60 and turn < 340:
            next_action = expand(shipyard)
        elif remaining_kore <= shipyard.max_spawn * 10 and shipyard.ship_count >= 2:
            # can't spawn more, need resources
            next_action = mine(shipyard)
        elif shipyard.ship_count < 2 and turn < 380 and remaining_kore >= shipyard.max_spawn * 10:
            # no ships to send and time remaining, let's spawn
            spawn_qty = min(shipyard.max_spawn, int(me.kore / 10))
            next_action = ShipyardAction.spawn_ships(spawn_qty)
            remaining_kore -= spawn_qty * 10
        else:
            if shipyard.ship_count >= 2 and randint(1, 10) < 3:
                # let's send the ships somewhere
                next_action = mine(shipyard)
            elif remaining_kore >= shipyard.max_spawn * 10:
                spawn_qty = min(shipyard.max_spawn, int(me.kore / 10))
                next_action = ShipyardAction.spawn_ships(spawn_qty)
                remaining_kore -= spawn_qty * 10
                # let's spawn
            else:
                next_action = None
        if next_action is not None:
            shipyard.next_action = next_action

    return me.next_actions