import json

# 100% Autonomous - 0% Latency - 0% Packet Loss - Even Spawning

save_plan_file_name = "../testing_plans/legacy_control_even_spawning.plan"

control_methods = ["fixed timings", "demand scheduling"]
junctions = ["simple_Y_junction.junc", "simple_T_junction.junc", "simple_X_junction.junc", "scale_library_pub_junction.junc"]
random_seed_values = [1788621521, 1774553582, 1490597230]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]
steps = 4500

actions = [
    [2, 1],
    [2, 1, 4],
    [2, 1, 8, 4],
    [35, 56, 22]
]

action_durations = [
    [300, 300],
    [300, 300, 300],
    [300, 300, 300, 300],
    [300, 300, 300]
]

action_paths = [
    [[5], [7]],
    [[3], [5], [10]],
    [[16], [18], [20], [13]],
    [[7, 8], [10, 11], [13, 14]]
]

plan = {}
uid = 0

for control_method in control_methods:
    for index, junction in enumerate(junctions):
        for random_seed_value in random_seed_values:
            for spawn_time_delta_value in spawn_time_delta_values:

                plan[str(uid)] = {
                    "RunUID": "Legacy_even_spawning_control_method_" + control_method.replace(" ", "_") + "_junction_" + junction[:-5] + "_seed_" + str(random_seed_value) + "_spawn_rate_" + str(round(60 / spawn_time_delta_value, 2)) + "cpm",
                    "RunType": control_method,
                    "Junction": junction,
                    "SimulationConfig": "final_testing/even_spawning/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config",
                    "Steps": steps,
                    "Actions": actions[index],
                    "ActionDurations": action_durations[index],
                    "ActionPaths": action_paths[index],
                    "RandomSeed": random_seed_value,
                    "CPM": (round(60/spawn_time_delta_value, 2)),
                    "SpawningChange": "even"
                }

                uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)

# 100% Autonomous - 0% Latency - 0% Packet Loss - Uneven Spawning

save_plan_file_name = "../testing_plans/legacy_control_uneven_spawning.plan"

control_methods = ["fixed timings", "demand scheduling"]
junctions = ["simple_T_junction.junc", "simple_X_junction.junc"]
config_folders = [["simple_T/bottom/", "simple_T/side/"], ["simple_X/single/", "simple_X/double/"]]
spawning_change = [["bottom", "side"], ["single", "double"]]
random_seed_values = [1788621521, 1774553582, 1490597230]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]
steps = 4500

actions = [
    [2, 1, 4],
    [2, 1, 8, 4],
]

action_durations = [
    [300, 300, 300],
    [300, 300, 300, 300],
]

action_paths = [
    [[3], [5], [10]],
    [[16], [18], [20], [13]],
]

plan = {}
uid = 0

for control_method in control_methods:
    for junction_index, junction in enumerate(junctions):
        for spawning_change_index, config_folder in enumerate(config_folders[junction_index]):
            for random_seed_value in random_seed_values:
                for spawn_time_delta_value in spawn_time_delta_values:
                    plan[str(uid)] = {
                        "RunUID": "Legacy_uneven_spawning_control_method_" + control_method.replace(" ", "_") + "_spawn_change_" + str(spawning_change[junction_index][spawning_change_index]) + "_junction_" + junction[:-5] + "_seed_" + str(random_seed_value) + "_spawn_rate_" + str(round(60/spawn_time_delta_value, 2)) + "cpm",
                        "RunType": control_method,
                        "Junction": junction,
                        "SimulationConfig": "final_testing/uneven_spawning/" + config_folder + "seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config",
                        "Steps": steps,
                        "Actions": actions[junction_index],
                        "ActionDurations": action_durations[junction_index],
                        "ActionPaths": action_paths[junction_index],
                        "RandomSeed": random_seed_value,
                        "CPM": (round(60/spawn_time_delta_value, 2)),
                        "SpawningChange": spawning_change[junction_index][spawning_change_index]
                    }

                    uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)


