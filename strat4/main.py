import math
from random import choice, randint, randrange, sample, seed, random

from kaggle_environments.envs.kore_fleets.kore_fleets import get_closest_enemy_shipyard, Point, Direction, \
    ShipyardAction, Board, get_shortest_flight_path_between
# from kaggle_environments.envs.kore_fleets.helpers import *
from extra_helpers import min_ship_count_for_flight_plan_len, collection_rate_for_ship_count, spawn_ships, add_log
# from kaggle_environments.envs.kore_fleets.kore_fleets import Point


def agent(obs, config):

    board = Board(obs, config)
    me = board.current_player
    remaining_kore = me.kore
    shipyards = me.shipyards
    convert_cost = board.configuration.convert_cost
    size = board.configuration.size
    spawn_cost = board.configuration.spawn_cost
    turn = board.step

    add_log("turn is " + str(turn))

    invading_fleet_size = 75
    convert_cost_buffer = 80
    mining_search_radius = 10
    defence_radius = 7

    # opponent_shipyards = board.opponents[0].shipyards[0].position

    shipyards = sample(shipyards, len(shipyards))
    for shipyard in shipyards:
        feel_shift = 0  # and pickup turn19 B9 or 1 and 17 opposite dir
        if turn == 2:
            shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(2, "E")
        elif turn == 4:
            shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(2, "W")
        elif turn == 7:
            shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(3, "N" + str(feel_shift + 3) + "E")
        elif turn == 9:
            shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(3, "N" + str(feel_shift + 2) + "E")
        elif turn == 11:
            shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(3, "N" + str(feel_shift + 1) + "E")
        elif turn == 13:
            shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(3, "N" + str(feel_shift) + "E")
        elif turn == 16:
            # shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(shipyard.ship_count, "S")
            shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(shipyard.ship_count, "N9S")
            # shipyard.next_action = spawn_ships(shipyard, remaining_kore, spawn_cost)
        else:
            shipyard.next_action = ShipyardAction.spawn_ships(min(shipyard.max_spawn, int(me.kore / 10)))
        if turn < 25:
            print(turn, shipyard.position, shipyard.ship_count, shipyard.max_spawn, "-->", shipyard.next_action)
    return me.next_actions