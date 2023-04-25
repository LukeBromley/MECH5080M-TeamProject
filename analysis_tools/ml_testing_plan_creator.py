import json

# # EVEN SPAWNING - ALL AUTONOMOUS DRIVER - STABLE NETWORK
#
# save_plan_file_name = "../testing_plans/trial_test_ml.plan"
#
# # junctions = ["simple_Y_junction.junc", "simple_T_junction.junc", "simple_X_junction.junc", "scale_library_pub_junction.junc"]
# junctions = ["simple_T_junction.junc"]
# # ml_model = ["simple_Y_junction_saved_model", "simple_T_junction_saved_model", "simple_X_junction_saved_model", "scale_library_pub_junction_saved_model"]
# ml_model = ["saved_model_simple_T_junction"]
# random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
# spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]
# steps = 4500
# human_drivers_visible = True
# network_latency = 0
# packet_loss_perc = 0
#
# plan = {}
# uid = 0
#
# for index, junction in enumerate(junctions):
#     print(junction)
#     for random_seed_value in random_seed_values:
#         print(random_seed_value)
#         for spawn_time_delta_value in spawn_time_delta_values:
#             print(spawn_time_delta_value)
#
#             plan[str(uid)] = {
#                 "RunUID": str(junction) + "_" + str(random_seed_value) + "_" + str(spawn_time_delta_value),
#                 "RunType": "junction",
#                 "Junction": junction,
#                 "SimulationConfig": "final_testing/even_spawning/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60 / spawn_time_delta_value, 2)) + "cpm.config",
#                 "MachineLearningModel": ml_model[index],
#                 "Steps": steps,
#                 "HumanDriversVisible": human_drivers_visible,
#                 "NetworkLatency": network_latency,
#                 "PacketLoss": packet_loss_perc
#             }
#
#             uid += 1
#
# with open(save_plan_file_name, "w") as file:
#     json.dump(plan, file)
#
# # EVEN SPAWNING - MIXED DRIVER TYPE - STABLE NETWORK
#
# save_plan_file_name = "../testing_plans/ml_control_mixed_drivers.plan"
#
# autonomous_percentage_values = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
#
# junctions = ["simple_T_junction.junc"]
# ml_model = ["simple_T_junction_saved_model"]
# random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
# spawn_time_delta_values = [30, 15, 10, 7.5, 6, 5, 4.285714286, 3.75, 3.333333333, 3, 2.727272727, 2.5, 2.307692308, 2.142857143, 2, 1.875, 1.764705882, 1.666666667, 1.578947368, 1.5, 1.428571429,1.363636364, 1.304347826, 1.25, 1.2, 1.153846154, 1.111111111, 1.071428571, 1.034482759, 1]
# steps = 9000
# human_drivers_visible = False
# network_latency = 0
# packet_loss_perc = 0
#
# plan = {}
# uid = 0
#
# for autonomous_percentage_value in autonomous_percentage_values:
#     print(autonomous_percentage_value)
#     for random_seed_value in random_seed_values:
#         print(random_seed_value)
#         for spawn_time_delta_value in spawn_time_delta_values:
#             print(spawn_time_delta_value)
#
#             plan[str(uid)] = {
#                 "RunUID": str(autonomous_percentage_value) + "_" + str(random_seed_value) + "_" + spawn_time_delta_value,
#                 "RunType": "junction",
#                 "Junction": junctions[0],
#                 "SimulationConfig": "final_testing/mixed_driver_type/" + str(autonomous_percentage_value) + "_perc_autonomous/seed_" + str(random_seed_value) + "/" + str(round(60 / spawn_time_delta_value)) + "cpm.config",
#                 "MachineLearningModel": ml_model[0],
#                 "Steps": steps,
#                 "HumanDriversVisible": human_drivers_visible,
#                 "NetworkLatency": network_latency,
#                 "PacketLoss": packet_loss_perc
#             }
#
#             uid += 1
#
# with open(save_plan_file_name, "w") as file:
#     json.dump(plan, file)
#
# EVEN SPAWNING - AI DRIVERS - LATENCY

save_plan_file_name = "../testing_plans/ml_control_latency.plan"

junctions = ["simple_T_junction.junc"]
ml_model = ["saved_model_simple_T_junction"]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [60, 30, 15, 7.5, 3.75]
steps = 4500
human_drivers_visible = True
network_latency = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
packet_loss_perc = 0

plan = {}
uid = 0

for latency in network_latency:
    print(latency)
    for random_seed_value in random_seed_values:
        print(random_seed_value)
        for spawn_time_delta_value in spawn_time_delta_values:
            print(spawn_time_delta_value)

            plan[str(uid)] = {
                "RunUID": str(latency) + "_" + str(random_seed_value) + "_" + str(spawn_time_delta_value) + "cpm",
                "RunType": "junction",
                "Junction": junctions[0],
                "SimulationConfig": "final_testing/even_spawning/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60 / spawn_time_delta_value, 2)) + "cpm.config",
                "MachineLearningModel": ml_model[0],
                "Steps": steps,
                "HumanDriversVisible": human_drivers_visible,
                "NetworkLatency": latency,
                "PacketLoss": packet_loss_perc
            }

            uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)


# EVEN SPAWNING - AI DRIVERS - PACKET LOSS

save_plan_file_name = "../testing_plans/ml_control_packet_loss.plan"

junctions = ["simple_T_junction.junc"]
ml_model = ["saved_model_simple_T_junction"]
random_seed_values = [1788621521, 1774553582, 1490597230, 997415346, 1433874439]
spawn_time_delta_values = [60, 30, 15, 7.5, 3.75]
steps = 4500
human_drivers_visible = True
network_latency = 0
packet_loss_perc = [0, 2, 4, 6, 8, 10, 20, 30, 40, 50]

plan = {}
uid = 0

for packet_loss in packet_loss_perc:
    print(packet_loss)
    for random_seed_value in random_seed_values:
        print(random_seed_value)
        for spawn_time_delta_value in spawn_time_delta_values:
            print(spawn_time_delta_value)

            plan[str(uid)] = {
                "RunUID": str(packet_loss*100) + "_" + str(random_seed_value) + "_" + str(spawn_time_delta_value) + "cpm",
                "RunType": "junction",
                "Junction": junctions[0],
                "SimulationConfig": "final_testing/even_spawning/autonomous/seed_" + str(random_seed_value) + "/" + str(round(60 / spawn_time_delta_value, 2)) + "cpm.config",
                "MachineLearningModel": ml_model[0],
                "Steps": steps,
                "HumanDriversVisible": human_drivers_visible,
                "NetworkLatency": network_latency,
                "PacketLoss": packet_loss
            }

            uid += 1

with open(save_plan_file_name, "w") as file:
    json.dump(plan, file)
