import os
import json
import results_spreadsheet_maker

results_location = "../results/ml_control_uneven_spawning_simple_X_TESTED"
run_folders = [x[0] for x in os.walk(results_location)]

all_results = []

for folder in run_folders[1:]:
    with open(folder + "/testing_run_parameters.json", "r") as file:
        all_results.append(json.load(file))

results_spreadsheet_maker.main(all_results, wb_name=results_location + "/Summary_Results_" + results_location.split("/")[-1] +".xlsx")

