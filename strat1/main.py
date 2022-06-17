import math
from random import choice, randint, randrange, sample, seed, random

from kaggle_environments.envs.kore_fleets.kore_fleets import get_closest_enemy_shipyard, Point, Direction, \
    ShipyardAction, Board, get_shortest_flight_path_between
# from kaggle_environments.envs.kore_fleets.helpers import *
from extra_helpers import min_ship_count_for_flight_plan_len, collection_rate_for_ship_count, spawn_ships, add_log
# from kaggle_environments.envs.kore_fleets.kore_fleets import Point


###############################################################################
## attack.py

def should_attack(board, shipyard, remaining_kore, spawn_cost, invading_fleet_size):
    closest_enemy_shipyard = get_closest_enemy_shipyard(board, shipyard.position, board.current_player)
    dist_to_closest_enemy_shipyard = 100 if not closest_enemy_shipyard else \
        shipyard.position.distance_to(closest_enemy_shipyard.position, board.configuration.size)
    if (closest_enemy_shipyard
            and (closest_enemy_shipyard.ship_count < 20 or dist_to_closest_enemy_shipyard < 15)
            and (remaining_kore >= spawn_cost or shipyard.ship_count >= invading_fleet_size)
            and (board.step > 300 or dist_to_closest_enemy_shipyard < 12)):
        return True
    return False


###############################################################################
## defend.py
def should_defend(board, me, shipyard, radius=7):
    loc = shipyard.position
    for i in range(1-radius, radius):
        for j in range(1-radius, radius):
            pos = loc.translate(Point(i, j), board.configuration.size)
            if ((board.cells.get(pos).fleet is not None)
                    and (board.cells.get(pos).fleet.ship_count > 50)
                    and (board.cells.get(pos).fleet.player_id != me.id)
                    and (board.cells.get(pos).fleet.ship_count > shipyard.ship_count)):
                return True
    return False


###############################################################################
## build.py
def should_build(shipyard, remaining_kore):
    if remaining_kore > 500 and shipyard.max_spawn > 5:
        return True
    return False


def check_location(board, loc, me):
    if board.cells.get(loc).shipyard and board.cells.get(loc).shipyard.player.id == me.id:
        return 0
    kore = 0
    for i in range(-6, 7):
        for j in range(-6, 7):
            pos = loc.translate(Point(i, j), board.configuration.size)
            kore += board.cells.get(pos).kore or 0
    return kore


def build_new_shipyard(shipyard, board, me, convert_cost, search_radius=3):
    best_dir = 0
    best_kore = 0
    best_gap1 = 0
    best_gap2 = 0
    for i in range(4):
        next_dir = (i + 1) % 4
        for gap1 in range(0, search_radius, 1):
            for gap2 in range(0, search_radius, 1):
                enemy_shipyard_close = False
                diff1 = Direction.from_index(i).to_point() * gap1
                diff2 = Direction.from_index(next_dir).to_point() * gap2
                diff = diff1 + diff2
                pos = shipyard.position.translate(diff, board.configuration.size)
                for shipyard in board.shipyards.values():
                    if ((shipyard.player_id != me.id)
                            and (pos.distance_to(shipyard.position, board.configuration.size) < 4)):
                        enemy_shipyard_close = True
                if enemy_shipyard_close:
                    continue
                h = check_location(board, pos, me)
                if h > best_kore:
                    best_kore = h
                    best_gap1 = gap1
                    best_gap2 = gap2
                    best_dir = i
    gap1 = str(best_gap1)
    gap2 = str(best_gap2)
    next_dir = (best_dir + 1) % 4
    flight_plan = Direction.list_directions()[best_dir].to_char() + gap1
    flight_plan += Direction.list_directions()[next_dir].to_char() + gap2
    flight_plan += "C"
    return ShipyardAction.launch_fleet_with_flight_plan(max(convert_cost + 30, int(shipyard.ship_count/2)), flight_plan)


###############################################################################
## mine.py
def should_mine(shipyard, best_fleet_size):
    if shipyard.ship_count >= best_fleet_size:
        return True
    return False


def check_path(board, start, dirs, dist_a, dist_b, collection_rate, L=False):
    kore = 0
    npv = .99
    current = start
    steps = 2 * (dist_a + dist_b + 2)
    for idx, d in enumerate(dirs):
        if L and idx==2:
            break
        for _ in range((dist_a if idx % 2 == 0 else dist_b) + 1):
            current = current.translate(d.to_point(), board.configuration.size)
            kore += int((board.cells.get(current).kore or 0) * collection_rate)
            final_kore = int((board.cells.get(current).kore or 0) * collection_rate)
    if L: kore = (kore) + (kore*(1-collection_rate)) - final_kore
    return math.pow(npv, steps) * kore / steps


def get_circular_flight_plan(gap1, gap2, start_dir):
    flight_plan = Direction.list_directions()[start_dir].to_char()
    if int(gap1):
        flight_plan += gap1
    next_dir = (start_dir + 1) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    if int(gap2):
        flight_plan += gap2
    next_dir = (next_dir + 1) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    if int(gap1):
        flight_plan += gap1
    next_dir = (next_dir + 1) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    return flight_plan


def get_L_flight_plan(gap1, gap2, start_dir):
    flight_plan = Direction.list_directions()[start_dir].to_char()
    if int(gap1):
        flight_plan += gap1
    next_dir = (start_dir + 1) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    if int(gap2):
        flight_plan += gap2
    next_dir = (next_dir + 2) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    if int(gap2):
        flight_plan += gap2
    next_dir = (next_dir - 1) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    return flight_plan


def get_rectangle_flight_plan(gap, start_dir):
    flight_plan = Direction.list_directions()[start_dir].to_char()
    next_dir = (start_dir + 1) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    if int(gap):
        flight_plan += gap
    next_dir = (next_dir + 1) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    next_dir = (next_dir + 1) % 4
    flight_plan += Direction.list_directions()[next_dir].to_char()
    return flight_plan


def check_flight_paths(board, shipyard, search_radius):
    best_h = 0
    best_gap1 = 1
    best_gap2 = 1
    best_dir = board.step % 4
    for i in range(4):
        dirs = Direction.list_directions()[i:] + Direction.list_directions()[:i]
        for gap1 in range(0, search_radius):
            for gap2 in range(0, search_radius):
                fleet_size = min_ship_count_for_flight_plan_len(7)
                h = check_path(board, shipyard.position, dirs, gap1, gap2, collection_rate_for_ship_count(fleet_size), L=False)
                if h/fleet_size > best_h:
                    best_h = h/fleet_size
                    best_flight_plan = get_circular_flight_plan(str(gap1), str(gap2), i)
                    best_fleet_size = fleet_size
                h = check_path(board, shipyard.position, dirs, gap1, gap2, collection_rate_for_ship_count(collection_rate_for_ship_count(fleet_size)), L=True)
                if h/fleet_size > best_h:
                    best_h = h/fleet_size
                    best_flight_plan = get_L_flight_plan(str(gap1), str(gap2), i)
                    best_fleet_size = fleet_size
                if gap1!=0:
                    continue
                fleet_size = min_ship_count_for_flight_plan_len(5)
                h = check_path(board, shipyard.position, dirs, gap1, gap2, collection_rate_for_ship_count(fleet_size), L=False)
                if h/fleet_size > best_h:
                    best_h = h/fleet_size
                    best_flight_plan = get_rectangle_flight_plan(str(gap2), i)
                    best_fleet_size = fleet_size
    return best_fleet_size, best_flight_plan


###############################################################################
## mine.py
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

    shipyards = sample(shipyards, len(shipyards))
    for shipyard in shipyards:

        best_fleet_size, best_flight_plan = check_flight_paths(board, shipyard, mining_search_radius)

        if should_defend(board, me, shipyard, defence_radius):
            if remaining_kore >= spawn_cost:
                shipyard.next_action = spawn_ships(shipyard, remaining_kore, spawn_cost)

        elif should_attack(board, shipyard, remaining_kore, spawn_cost, invading_fleet_size):
            if shipyard.ship_count >= invading_fleet_size:
                closest_enemy_shipyard = get_closest_enemy_shipyard(board, shipyard.position, board.current_player)
                flight_plan = get_shortest_flight_path_between(shipyard.position, closest_enemy_shipyard.position, size)
                shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(invading_fleet_size, flight_plan)
            elif remaining_kore >= spawn_cost:
                shipyard.next_action = spawn_ships(shipyard, remaining_kore, spawn_cost)

        elif should_build(shipyard, remaining_kore):
            if shipyard.ship_count >= convert_cost + convert_cost_buffer:
                shipyard.next_action = build_new_shipyard(shipyard, board, me, convert_cost)
            elif remaining_kore >= spawn_cost:
                shipyard.next_action = spawn_ships(shipyard, remaining_kore, spawn_cost)

        elif should_mine(shipyard, best_fleet_size):
            shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(best_fleet_size, best_flight_plan)

        elif (remaining_kore > spawn_cost):
            shipyard.next_action = spawn_ships(shipyard, remaining_kore, spawn_cost)

        elif (len(me.fleet_ids) == 0 and shipyard.ship_count <= 22) and len(shipyards)==1:
            if remaining_kore > 11:
                shipyard.next_action = spawn_ships(shipyard, remaining_kore, spawn_cost)
            else:
                direction = Direction.NORTH
                if shipyard.ship_count > 0:
                    shipyard.next_action = ShipyardAction.launch_fleet_with_flight_plan(shipyard.ship_count, direction.to_char())

    return me.next_actions