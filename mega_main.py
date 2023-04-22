from platform import system

from gui.junction_visualiser import JunctionVisualiser

if system() == 'Windows':
    import sys
    sys.path.append('./')

from machine_learning.machine_learning_manager import MachineLearningManager
from machine_learning.trained_model_tester import TrainedModelTester
from machine_learning.fixed_timings_tester import FixedTimingsTester


# MEGAMAIN - Choose between automated training and automated testing of pretrained models.
# MEGAMAINTEST - Choose between automated training and automated testing of pretrained models.
if __name__ == "__main__":
    # iteration_file = "ml_training_plan.csv"
    # iterations = MachineLearningManager(iteration_file)
    tester_file = "ml_testing_plan.json"
    testing = TrainedModelTester(tester_file)
    # tester_file = "ft_testing_plan.json"
    # testing = FixedTimingsTester(tester_file)
