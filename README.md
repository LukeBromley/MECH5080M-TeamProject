# MECH5080M-TeamProject
Git repository for Group 30's Team Project for MECH5080M Team Project (39050) 2022/23 at the University of Leeds.

## mega_main.py
This script can be used to run multiple machine learning runs in one go. 

It requires a csv file in the same format as iteration_file.csv provided which contains the necessary config files and machine learning parameters for each model that will be trained.
Additionally, the corresponding configs file must be placed within the expected directory:

A .junc junction file should be placed within ./junctions

A .config simulation config file should be placed in ./configurations/simulation_config

A machine learning config file should be placed in ./configurations/machine_learning_config

Finally, the machine learning config index must be provided to select the ML parameters for each run.