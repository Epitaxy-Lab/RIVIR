import matplotlib
import datetime, warnings
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def assign_points(coords):
    x1 = min(coords[0][0], coords[1][0])
    x2 = max(coords[0][0], coords[1][0])
    y1 = min(coords[0][1], coords[1][1])
    y2 = max(coords[0][1], coords[1][1])
    return x1, x2, y1, y2

class coord():
    def __init__(self, rect):
        self.x1, self.x2, self.y1, self.y2 = assign_points(rect)

class plot_obj():
    def __init__(self, rect_coords, canvas):
        self.fig = plt.Figure()
        self.fig.autofmt_xdate()
        self.axis = self.fig.add_subplot(111)
        self.graph = FigureCanvasTkAgg(self.fig, canvas)
        self.rects = [coord(rect_coords)]
        self.plot_vals = [([],[])]
        self.max_int = 0
        self.min_int = 0

    def add_line(self, rect_coords):
        self.rects.append(coord(rect_coords))
        self.plot_vals.append(([],[]))


    def update_plot(self):
        self.axis.cla()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.axis.set_xticklabels(self.plot_vals[0][1], rotation=30)
        self.axis.set_xlabel("Time")
        self.axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        longest_time = self.plot_vals[0][1]
        if(len(longest_time) > 1):
            self.axis.set_xlim(min(longest_time), max(longest_time))
            self.axis.set_ylim(self.min_int * .8, self.max_int * 1.15)
        else:
            self.axis.set_xlim(0, 1)
            self.axis.set_ylim(0, 1)

    def draw_plot(self):
        for values in self.plot_vals:
            self.axis.plot_date(values[1], values[0], linestyle='-', marker=',')
        self.graph.draw()
        self.graph.get_tk_widget().pack(side='top', fill='both', expand=1);

    def update_val(self, ind, pixels):
        avg_val = n = 0
        corners = self.rects[ind]
        for x in range(corners.x1, corners.x2):
            for y in range(corners.y1, corners.y2):
                avg_val += sum(pixels[x][y])
                n += 1
        avg_val = avg_val / n

        if avg_val > self.max_int:
            self.max_int = avg_val
        if avg_val < self.min_int:
            self.min_int = avg_val

        now = datetime.datetime.now()

        self.plot_vals[ind][0].append(avg_val)
        self.plot_vals[ind][1].append(now)

    def update_vals(self, pixels):
        for i in range(len(self.rects)):
            self.update_val(i, pixels)

        self.update_plot()
