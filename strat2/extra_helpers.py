from kaggle_environments.envs.kore_fleets.helpers import Direction


# a flight plan
def build_flight_plan(dir_idx, size):
    flight_plan = ""
    for i in range(4):
        flight_plan += Direction.from_index((dir_idx + i) % 4).to_char()
        if not i == 3:
            flight_plan += str(size)
    return flight_plan
