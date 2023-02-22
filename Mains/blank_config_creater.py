from Library.FileManagement import Configuration, FileManagement
conf = Configuration()
file_manager = FileManagement()
file_manager.save_config_file("blank_config.config", conf)
