from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from machine_learning.machine_learning_manager import MachineLearningManager
from machine_learning.trained_model_tester import TrainedModelTester


# MEGAMAIN - Choose between automated training and automated testing of pretrained models.
# MEGAMAINTEST - Choose between automated training and automated testing of pretrained models.
if __name__ == "__main__":
    #iteration_file = "iteration_file.csv"
    #iterations = MachineLearningManager(iteration_file)
    tester_file = "testing_trained_model.csv"
    testing = TrainedModelTester(tester_file)