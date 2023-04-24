import os
import json
from statistics import mean

results_location = "../results/test_TESTED(1)"
run_folders = [x[0] for x in os.walk(results_location)]
spawn_time_delta_values = [90, 60, 45, 30, 20, 15, 10, 5, 4, 3, 2]

all_results = []

for folder in run_folders[1:]:
    with open(folder + "/testing_run_parameters.json", "r") as file:
        all_results.append(json.load(file))

all_results_per_cpm = {}

for result in all_results:
    cpm = round(float(result["RunUID"].split("_")[-1][:-3]), 2)

    if str(cpm) in all_results_per_cpm.keys():
        all_results_per_cpm[str(cpm)].append(result)
    else:
        all_results_per_cpm[str(cpm)] = [result]

number_of_vehicles = []
for spawn_time_delta_value in spawn_time_delta_values:
    vehicles_spawned = []
    for result in all_results_per_cpm[str(round(60 / spawn_time_delta_value, 2))]:
        vehicles_spawned.append(result["Number Of Vehicles Spawned"])
    number_of_vehicles.append(mean(vehicles_spawned))
    print(mean(vehicles_spawned))

