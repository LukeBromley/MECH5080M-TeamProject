import json

save_plan_file_name = "../testing_plans/legacy_control_even_spawning.plan"

control_methods = ["fixed timing", "demand scheduling"]
junctions = ["simple_Y_junction.junc", "simple_T_junction.junc", "simple_X_junction.junc", "scale_library_pub_junction.junc"]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [30, 15, 10, 7.5, 6, 5, 4.285714286, 3.75, 3.333333333, 3, 2.727272727, 2.5, 2.307692308, 2.142857143, 2, 1.875, 1.764705882, 1.666666667, 1.578947368, 1.5, 1.428571429,1.363636364, 1.304347826, 1.25, 1.2, 1.153846154, 1.111111111, 1.071428571, 1.034482759, 1]
steps = 9000

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
                    "RunUID": uid,
                    "RunType": control_method,
                    "Junction": junction,
                    "SimulationConfig": "final_testing/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value)) + "cpm.config",
                    "Steps": steps,
                    "Actions": actions[index],
                    "ActionDurations": action_durations[index],
                    "ActionPaths": action_paths[index],
                }

                uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)
