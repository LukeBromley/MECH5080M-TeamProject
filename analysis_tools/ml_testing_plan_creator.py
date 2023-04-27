import json

# 100% Autonomous - 0% Latency - 0% Packet Loss - Even Spawning

save_plan_file_name = "../testing_plans/ml_control_even_spawning.plan"

junctions = ["simple_Y_junction.junc", "simple_T_junction.junc", "simple_X_junction.junc", "scale_library_pub_junction.junc"]
ml_model = ["saved_model_simple_Y_junction", "saved_model_simple_T_junction", "saved_model_simple_X_junction", "saved_model_scale_library_pub_junction"]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]

steps = 4500
human_drivers_visible = True
network_latency = 0
packet_loss_perc = 0

plan = {}
uid = 0

for index, junction in enumerate(junctions):
    for random_seed_value in random_seed_values:
        for spawn_time_delta_value in spawn_time_delta_values:

            plan[str(uid)] = {
                "RunUID": "ML_EvenSpawning_AllAI_StableNet_junction_" + str(junction) + "_seed_" + str(random_seed_value) + "_spawn_rate_" + str(round(60 / spawn_time_delta_value, 2)) + "cpm",
                "RunType": "junction",
                "Junction": junction,
                "SimulationConfig": "final_testing/even_spawning/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60 / spawn_time_delta_value, 2)) + "cpm.config",
                "MachineLearningModel": ml_model[index],
                "Steps": steps,
                "RandomSeed": random_seed_value,
                "CPM": (round(60 / spawn_time_delta_value, 2)),
                "HumanDriversVisible": human_drivers_visible,
                "NetworkLatency": network_latency,
                "PacketLoss": packet_loss_perc,
                "SpawningChange": "even"
            }

            uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)

# 100% Autonomous - 0% Latency - 0% Packet Loss - Uneven Spawning

save_plan_file_name = "../testing_plans/ml_control_uneven_spawning.plan"

junctions = ["simple_T_junction.junc", "simple_X_junction.junc"]
ml_model = ["saved_model_simple_T_junction", "saved_model_simple_X_junction"]
config_folders = [["simple_T/bottom/", "simple_T/side/"], ["simple_X/single/", "simple_X/double/"]]
spawning_change = [["bottom", "side"], ["single", "double"]]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]

steps = 4500
human_drivers_visible = True
network_latency = 0
packet_loss_perc = 0

plan = {}
uid = 0

for junction_index, junction in enumerate(junctions):
    for spawning_change_index, config_folder in enumerate(config_folders[junction_index]):
        for random_seed_value in random_seed_values:
            for spawn_time_delta_value in spawn_time_delta_values:

                plan[str(uid)] = {
                    "RunUID": "ML_UnevenSpawning_AllAI_StableNet_junction_" + str(junction) + "_seed_" + str(random_seed_value) + "_spawn_rate_" + str(round(60 / spawn_time_delta_value, 2)) + "cpm",
                    "RunType": "junction",
                    "Junction": junction,
                    "SimulationConfig": "final_testing/uneven_spawning/" + config_folder + "seed_" + str(random_seed_value) + "/" + str(round(60 / spawn_time_delta_value, 2)) + "cpm.config",
                    "MachineLearningModel": ml_model[junction_index],
                    "Steps": steps,
                    "RandomSeed": random_seed_value,
                    "CPM": (round(60 / spawn_time_delta_value, 2)),
                    "HumanDriversVisible": human_drivers_visible,
                    "NetworkLatency": network_latency,
                    "PacketLoss": packet_loss_perc,
                    "SpawningChange": spawning_change[junction_index][spawning_change_index]
                }

                uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)

# ?% Autonomous - 0% Latency - 0% Packet Loss - Even Spawning

save_plan_file_name = "../testing_plans/ml_control_human.plan"

autonomous_percentage_values = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
junctions = ["simple_T_junction.junc"]
ml_model = ["saved_model_simple_T_junction"]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]

steps = 4500
human_drivers_visible = True
network_latency = 0
packet_loss_perc = 0

plan = {}
uid = 0

for autonomous_percentage_value in autonomous_percentage_values:
    for random_seed_value in random_seed_values:
        for spawn_time_delta_value in spawn_time_delta_values:

            plan[str(uid)] = {
                "RunUID": "ML_EvenSpawning_MixedDriver_StableNet_autonomous_perc_" + str(autonomous_percentage_value) + "_seed_" + str(random_seed_value) + "_spawn_rate_" + str(round(60/spawn_time_delta_value, 2)) + "cpm",
                "RunType": "junction",
                "Junction": junctions[0],
                "SimulationConfig": "final_testing/mixed_driver_type/" + str(autonomous_percentage_value) + "_perc_autonomous/seed_" + str(random_seed_value) + "/" + str(round(60/spawn_time_delta_value, 2)) + "cpm.config",
                "MachineLearningModel": ml_model[0],
                "Steps": steps,
                "RandomSeed": random_seed_value,
                "CPM": (round(60 / spawn_time_delta_value, 2)),
                "HumanDriversVisible": human_drivers_visible,
                "AutonomousPercentage": autonomous_percentage_value,
                "NetworkLatency": network_latency,
                "PacketLoss": packet_loss_perc
            }

            uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)

# 100% Autonomous - ?% Latency - 0% Packet Loss - Even Spawning

save_plan_file_name = "../testing_plans/ml_control_latency.plan"

junctions = ["simple_T_junction.junc"]
ml_model = ["saved_model_simple_T_junction"]

network_latency = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [60, 30, 15, 7.5, 3.75]

steps = 4500
human_drivers_visible = True
packet_loss_perc = 0

plan = {}
uid = 0

for latency in network_latency:
    for random_seed_value in random_seed_values:
        for spawn_time_delta_value in spawn_time_delta_values:

            plan[str(uid)] = {
                "RunUID": "ML_EvenSpawning_AllAI_LatencyNet_latency_" + str(latency) + "_seed_" + str(random_seed_value) + "_spawn_rate_" + str(round(60 / spawn_time_delta_value, 2)) + "cpm",
                "RunType": "junction",
                "Junction": junctions[0],
                "SimulationConfig": "final_testing/even_spawning/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60 / spawn_time_delta_value, 2)) + "cpm.config",
                "MachineLearningModel": ml_model[0],
                "Steps": steps,
                "RandomSeed": random_seed_value,
                "CPM": (round(60 / spawn_time_delta_value, 2)),
                "HumanDriversVisible": human_drivers_visible,
                "NetworkLatency": latency,
                "PacketLoss": packet_loss_perc
            }

            uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)


# 100% Autonomous - 0% Latency - ?% Packet Loss - Even Spawning

save_plan_file_name = "../testing_plans/ml_control_packet_loss.plan"

junctions = ["simple_T_junction.junc"]
ml_model = ["saved_model_simple_T_junction"]

packet_loss_perc = [0, 2, 4, 6, 8, 10, 20, 30, 40, 50]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [60, 30, 15, 7.5, 3.75]

steps = 4500
human_drivers_visible = True
network_latency = 0

plan = {}
uid = 0

for packet_loss in packet_loss_perc:
    for random_seed_value in random_seed_values:
        for spawn_time_delta_value in spawn_time_delta_values:

            plan[str(uid)] = {
                "RunUID": "ML_EvenSpawning_AllAI_PacketLossNet_packet_loss_" + str(packet_loss) + "_seed_" + str(random_seed_value) + "_spawn_rate_" + str(round(60 / spawn_time_delta_value, 2)) + "cpm",
                "RunType": "junction",
                "Junction": junctions[0],
                "SimulationConfig": "final_testing/even_spawning/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60 / spawn_time_delta_value, 2)) + "cpm.config",
                "MachineLearningModel": ml_model[0],
                "Steps": steps,
                "RandomSeed": random_seed_value,
                "CPM": (round(60 / spawn_time_delta_value, 2)),
                "HumanDriversVisible": human_drivers_visible,
                "NetworkLatency": network_latency,
                "PacketLoss": packet_loss
            }

            uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)
