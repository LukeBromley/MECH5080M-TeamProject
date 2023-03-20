import matplotlib.pyplot as plt

class Graph:
    def __init__(self, num_episodes_displayed, max_steps_displayed):
        self.num_episodes_displayed = num_episodes_displayed

        # to run GUI event loop
        plt.ion()

        # setting title
        plt.title("Reward", fontsize=20)

        # setting x-axis label and y-axis label
        plt.xlabel("Episode")
        plt.ylabel("Steps")

        # here we are creating sub plots
        self.figure, self.graph = plt.subplots(figsize=(10, 8))

        plt.ylim([0, max_steps_displayed])

        self.x = [i for i in range(self.num_episodes_displayed, 0, -1)]
        self.y = [0 for i in range(self.num_episodes_displayed)]

        self.line1, = self.graph.plot(self.x, self.y)

    def update(self, step):
        self.y.append(step)
        self.y = self.y[-self.num_episodes_displayed:]

        self.line1.set_xdata(self.x)
        self.line1.set_ydata(self.y)

        # drawing updated values
        self.figure.canvas.draw()

        # This will run the GUI event
        # loop until all UI events
        # currently waiting have been processed
        self.figure.canvas.flush_events()

    def hide_graph(self):
        plt.close()


if __name__ == "__main__":
    graph = Graph(100, 100)
    for i in range(100):
        graph.update(i)
