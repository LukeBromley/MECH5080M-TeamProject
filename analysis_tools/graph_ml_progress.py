import matplotlib.pyplot as plt


class Graph:
    def __init__(self, num_episodes_displayed, max_steps_displayed):
        self.num_episodes_displayed = num_episodes_displayed

        self.figure, self.ax = plt.subplots()
        self.figure.suptitle("Learning curve", fontsize=20)

        self.ax.set_xlabel('Actions taken')
        self.ax.set_ylabel('Mean reward')

        self.x = []
        self.y = []

        self.line, = self.ax.plot(self.x, self.y)

    def update(self, x: float, y: float):
        self.y.append(y)
        self.x.append(x)

        self.line.set_data(self.x, self.y)

        self.ax.set_ylim([min(self.y), max(self.y)])
        self.ax.set_xlim([min(self.x), max(self.x)])

        plt.pause(0.0001)
        self.figure.savefig("learning_curve.png")

    def hide_graph(self):
        plt.close()
