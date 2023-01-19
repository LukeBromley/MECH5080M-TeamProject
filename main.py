from Library.FileManagement import *

temp_config = Configuration(["A", "B"], 1, 8, -1, 1, 2, 5, 1, 2, 4)
filemanager = FileManagement()
filemanager.save_config_file("./Junction_Designs/Config.json", temp_config)

temp2_config = filemanager.load_config_file("./Junction_Designs/Config.json")
print()

