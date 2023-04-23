import os
import json

results_location = "../results/legacy_control_even_spawning_TESTED(4)"
run_folders = [x[0] for x in os.walk(results_location)]

all_results = []

for folder in run_folders[1:]:
    with open(folder + "/testing_run_parameters.json", "r") as file:
        all_results.append(json.load(file))

all_results_per_cpm = {}

for result in all_results:
    cpm = int(result["RunUID"].split("_")[-1][:-3])

    if str(cpm) in all_results_per_cpm.keys():
        all_results_per_cpm[str(cpm)].append(result)
    else:
        all_results_per_cpm[str(cpm)] = [result]


print()
