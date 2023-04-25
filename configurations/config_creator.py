from library.file_management import FileManagement
from copy import deepcopy as copy

# EVEN SPAWNING - ALL AUTONOMOUS

default_config_file_path = "simulation_config/cross_road.config"
save_config_folder_path = "simulation_config/final_testing/even_spawning/autonomous/"

random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2, 7.5, 3.75]

file_manager = FileManagement()
default_config = file_manager.load_sim_config_file(default_config_file_path)

for random_seed_value in random_seed_values:
    print(random_seed_value)

    for spawn_time_delta_value in spawn_time_delta_values:
        print(spawn_time_delta_value)

        new_config = copy(default_config)
        new_config.autonomous_driver_probability = 1
        new_config.random_seed = random_seed_value
        new_config.mean_spawn_time_per_hour = spawn_time_delta_value

        file_manager.save_sim_config_file(save_config_folder_path + "seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config", new_config)

# EVEN SPAWNING - MIXED DRIVER TYPE

default_config_file_path = "simulation_config/cross_road.config"
save_config_folder_path = "simulation_config/final_testing/even_spawning/mixed_driver_type/"

random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
autonomous_percentage_values = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2, 7.5, 3.75]

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

            file_manager.save_sim_config_file(save_config_folder_path + str(round(autonomous_percentage_value * 100)) + "_perc_autonomous/seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config", new_config)

# UNEVEN SPAWNING - AUTONOMOUS - SIMPLE T - SIDE

default_config_file_path = "simulation_config/cross_road.config"
save_config_folder_path = "simulation_config/final_testing/uneven_spawning/simple_T/side/"

random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]

file_manager = FileManagement()
default_config = file_manager.load_sim_config_file(default_config_file_path)

for random_seed_value in random_seed_values:
    print(random_seed_value)

    for spawn_time_delta_value in spawn_time_delta_values:
        print(spawn_time_delta_value)

        new_config = copy(default_config)
        new_config.autonomous_driver_probability = 1
        new_config.random_seed = random_seed_value
        new_config.mean_spawn_time_per_hour = {"3": spawn_time_delta_value, "12": 6, "7": 6}

        file_manager.save_sim_config_file(save_config_folder_path + "seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config", new_config)

# UNEVEN SPAWNING - AUTONOMOUS - SIMPLE T - BOTTOM

default_config_file_path = "simulation_config/cross_road.config"
save_config_folder_path = "simulation_config/final_testing/uneven_spawning/simple_T/bottom/"

random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]

file_manager = FileManagement()
default_config = file_manager.load_sim_config_file(default_config_file_path)

for random_seed_value in random_seed_values:
    print(random_seed_value)

    for spawn_time_delta_value in spawn_time_delta_values:
        print(spawn_time_delta_value)

        new_config = copy(default_config)
        new_config.autonomous_driver_probability = 1
        new_config.random_seed = random_seed_value
        new_config.mean_spawn_time_per_hour = {"3": 6, "12": 6, "7": spawn_time_delta_value}

        file_manager.save_sim_config_file(save_config_folder_path + "seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config", new_config)

# UNEVEN SPAWNING - AUTONOMOUS - SIMPLE X - SINGLE

default_config_file_path = "simulation_config/cross_road.config"
save_config_folder_path = "simulation_config/final_testing/uneven_spawning/simple_X/single/"

random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]

file_manager = FileManagement()
default_config = file_manager.load_sim_config_file(default_config_file_path)

for random_seed_value in random_seed_values:
    print(random_seed_value)

    for spawn_time_delta_value in spawn_time_delta_values:
        print(spawn_time_delta_value)

        new_config = copy(default_config)
        new_config.autonomous_driver_probability = 1
        new_config.random_seed = random_seed_value
        new_config.mean_spawn_time_per_hour = {"9": spawn_time_delta_value, "12": 6, "14": 6, "15": 6}

        file_manager.save_sim_config_file(save_config_folder_path + "seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config", new_config)

# UNEVEN SPAWNING - AUTONOMOUS - SIMPLE X - DOUBLE

default_config_file_path = "simulation_config/cross_road.config"
save_config_folder_path = "simulation_config/final_testing/uneven_spawning/simple_X/double/"

random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]

file_manager = FileManagement()
default_config = file_manager.load_sim_config_file(default_config_file_path)

for random_seed_value in random_seed_values:
    print(random_seed_value)

    for spawn_time_delta_value in spawn_time_delta_values:
        print(spawn_time_delta_value)

        new_config = copy(default_config)
        new_config.autonomous_driver_probability = 1
        new_config.random_seed = random_seed_value
        new_config.mean_spawn_time_per_hour = {"9": spawn_time_delta_value, "12": spawn_time_delta_value, "14": 6, "15": 6}

        file_manager.save_sim_config_file(save_config_folder_path + "seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config", new_config)
