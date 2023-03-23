from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from machine_learning.machine_learning_manager import MachineLearningManager

if __name__ == "__main__":
    iteration_file = "iteration_file.csv"
    iterations = MachineLearningManager(iteration_file)
    print("Complete")