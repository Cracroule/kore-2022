from random import randint

from kaggle_environments.envs.kore_fleets.helpers import *
from extra_helpers import build_flight_plan


def agent(obs, config):
    board = Board(obs, config)

    me = board.current_player
    turn = board.step
    spawn_cost = board.configuration.spawn_cost
    kore_left = me.kore

    for shipyard in me.shipyards:
        if shipyard.ship_count >= 50:
            flight_plan = build_flight_plan(randint(0, 3), randint(2, 9))
            action = ShipyardAction.launch_fleet_with_flight_plan(50, flight_plan)
            shipyard.next_action = action
        elif kore_left >= spawn_cost:
            action = ShipyardAction.spawn_ships(1)
            shipyard.next_action = action

    return me.next_actions