import json

save_plan_file_name = "../testing_plans/legacy_control_even_spawning.plan"

control_methods = ["fixed timings", "demand scheduling"]
junctions = ["simple_Y_junction.junc", "simple_T_junction.junc", "simple_X_junction.junc", "scale_library_pub_junction.junc"]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
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
    print(control_method)
    for index, junction in enumerate(junctions):
        print(junction)
        for random_seed_value in random_seed_values:
            print(random_seed_value)
            for spawn_time_delta_value in spawn_time_delta_values:
                print(spawn_time_delta_value)

                plan[str(uid)] = {
                    "RunUID": control_method.replace(" ", "_") + "_" + junction[:-5] + "_" + str(random_seed_value) + "_" + str(round(60/spawn_time_delta_value, 2)) + "cpm",
                    "RunType": control_method,
                    "Junction": junction,
                    "SimulationConfig": "final_testing/even_spawning/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config",
                    "Steps": steps,
                    "Actions": actions[index],
                    "ActionDurations": action_durations[index],
                    "ActionPaths": action_paths[index],
                }

                uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)