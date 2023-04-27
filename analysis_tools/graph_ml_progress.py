import matplotlib.pyplot as plt


class Graph:
    def __init__(self) -> object:
        self.figure, self.ax = plt.subplots()

        self.ax.set_xlabel('Number of actions')
        self.ax.set_ylabel('Mean reward')

        self.x = []
        self.y = []

        self.line, = self.ax.plot(self.x, self.y)

        plt.pause(0.001)

    def set_title(self, title: str = "Learning curve"):
        self.figure.suptitle(title, fontsize=20)
        self.figure.canvas.start_event_loop(0.001)
        self.figure.canvas.draw_idle()

    def update(self, x: float, y: float):
        self.y.append(y)
        self.x.append(x)

        self.line.set_data(self.x, self.y)

        self.ax.set_ylim([min(self.y), max(self.y)])
        # self.ax.set_xlim([min(self.x), max(self.x)])

        self.figure.canvas.start_event_loop(0.001)
        self.figure.canvas.draw_idle()

        self.figure.savefig("learning_curve.png")

    def add_vline(self, x: float) -> None:
        self.ax.axvline(x, linestyle='dashed', linewidth=1, color='k')
        self.figure.canvas.start_event_loop(0.001)
        self.figure.canvas.draw_idle()

    def hide_graph(self):
        plt.close()
