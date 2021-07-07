import matplotlib
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def assign_points(coords):
    x1 = min(coords[0][0], coords[1][0])
    x2 = max(coords[0][0], coords[1][0])
    y1 = min(coords[0][1], coords[1][1])
    y2 = max(coords[0][1], coords[1][1])
    return x1, x2, y1, y2

class plot_obj():
    def __init__(self, rect_coords, canvas):
        self.x1, self.x2, self.y1, self.y2 = assign_points(rect_coords)
        self.fig = plt.Figure()
        self.fig.autofmt_xdate()
        self.axis = self.fig.add_subplot(111)
        self.graph = FigureCanvasTkAgg(self.fig, canvas)
        self.vals = []
        self.time = []

    def update_plot(self):
        self.axis.cla()
        #self.axis.set_xticklabels(self.time, rotation=30)
        self.axis.set_xlabel("Time")
        self.axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        if(len(self.time) > 1):
            self.axis.set_xlim(min(self.time), max(self.time))
            self.axis.set_ylim(min(self.vals) * .8, max(self.vals) * 1.15)
        else:
            self.axis.set_xlim(0, 1)
            self.axis.set_ylim(0, 1)

    def draw_plot(self):
        self.axis.plot_date(self.time, self.vals, linestyle='-', marker=',')
        self.graph.draw()
        self.graph.get_tk_widget().pack(side='top', fill='both', expand=1);

    def update_vals(self, pixels):
        avg_val = n = 0
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                avg_val += sum(pixels[x][y])
                n += 1
        avg_val = avg_val / n
        now = datetime.datetime.now()

        self.vals.append(avg_val)
        self.time.append(now)

        self.update_plot()
