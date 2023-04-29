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
    # tester_file = "testing_plans/ml_control_uneven_spawning_simple_T.plan"
    # testing = TrainedModelTester(tester_file)
    # tester_file = "testing_plans/legacy_control_uneven_spawning.plan"
    # testing = FixedTimingsTester(tester_file)

    tester_file = "testing_plans/ml_control_even_spawning_simple_Y.plan"
    testing = TrainedModelTester(tester_file)

    tester_file = "testing_plans/ml_control_even_spawning_simple_T.plan"
    testing = TrainedModelTester(tester_file)

    tester_file = "testing_plans/ml_control_uneven_spawning_simple_T.plan"
    testing = TrainedModelTester(tester_file)

    tester_file = "testing_plans/ml_control_human.plan"
    testing = TrainedModelTester(tester_file)

    tester_file = "testing_plans/ml_control_latency.plan"
    testing = TrainedModelTester(tester_file)

    tester_file = "testing_plans/ml_control_packet_loss.plan"
    testing = TrainedModelTester(tester_file)


