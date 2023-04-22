from library.file_management import FileManagement
from copy import deepcopy as copy

default_config_file_path = "simulation_config/cross_road.config"
save_config_folder_path = "simulation_config/final_testing/mixed_driver_type/"

random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
autonomous_percentage_values = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0]
spawn_time_delta_values = [30, 15, 10, 7.5, 6, 5, 4.285714286, 3.75, 3.333333333, 3, 2.727272727, 2.5, 2.307692308, 2.142857143, 2, 1.875, 1.764705882, 1.666666667, 1.578947368, 1.5, 1.428571429,1.363636364, 1.304347826, 1.25, 1.2, 1.153846154, 1.111111111, 1.071428571, 1.034482759, 1]

file_manager = FileManagement()
default_config = file_manager.load_sim_config_file(default_config_file_path)

for autonomous_percentage_value in autonomous_percentage_values:
    print(autonomous_percentage_value)

    for random_seed_value in random_seed_values:
        print(random_seed_value)

        for spawn_time_delta_value in spawn_time_delta_values:
            print(spawn_time_delta_value)

            new_config = copy(default_config)
            new_config.autonomous_driver_probability = autonomous_percentage_value
            new_config.random_seed = random_seed_value
            new_config.mean_spawn_time_per_hour = spawn_time_delta_value

            file_manager.save_sim_config_file(save_config_folder_path + str(round(autonomous_percentage_value * 100)) + "_perc_autonomous/seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value)) + "cpm.config", new_config)


