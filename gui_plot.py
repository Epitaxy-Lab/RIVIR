import matplotlib
import datetime, warnings
import matplotlib as mpl
mpl.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.style.use("fast")

def assign_points(coords):
    x1 = min(coords[0][0], coords[1][0])
    x2 = max(coords[0][0], coords[1][0])
    y1 = min(coords[0][1], coords[1][1])
    y2 = max(coords[0][1], coords[1][1])
    return x1, x2, y1, y2

def resize_list(list):
    half_length = int(len(list) / 2)
    first_half = list[:half_length]
    first_half_split = first_half[::2]

    return first_half_split + list[half_length:]

class coord():
    def __init__(self, rect):
        self.x1, self.x2, self.y1, self.y2 = assign_points(rect)

class plot_obj():
    def __init__(self, rect_coords, canvas, color):
        self.fig = plt.Figure()
        self.fig.autofmt_xdate()
        self.axis = self.fig.add_subplot(111)
        #self.axis.axis("off")
        self.axis.set_facecolor("#e3f2fd")
        self.graph = FigureCanvasTkAgg(self.fig, canvas)
        self.graph.draw()
        self.graph.get_tk_widget().pack(side='right', fill='both', expand=1)
        self.bg = self.graph.copy_from_bbox(self.axis.bbox)
        self.rects = [coord(rect_coords)]
        self.plot_vals = [[[],[]]]
        self.plots = [self.axis.plot_date([], [], linestyle='-', marker=',', animated=True, color=color,alpha=0.3)]
        #self.num_resizes = [0]
        self.max_int = 0
        self.min_int = 0


        self.graph.draw()

    def add_line(self, rect_coords, color):
        self.rects.append(coord(rect_coords))
        self.plot_vals.append([[],[]])
        self.plots.append(self.axis.plot_date([], [], linestyle='-', marker=',', animated=True, color=color))

    def del_line(self, ind):
        del self.rects[ind]
        del self.plot_vals[ind]
        del self.plots[ind]
        return len(self.rects)

    def clear(self):
        new_vals = []
        for i in self.plot_vals:
            new_vals.append([[],[]])
        self.plot_vals = new_vals

    def update_plot(self):
        self.axis.set_xlim(left=0, right=self.plot_vals[0][0][-1])
        longest_time = self.plot_vals[0][1]
        if(len(longest_time) > 1):
            self.axis.set_xlim(longest_time[0], longest_time[-1])
            self.axis.set_ylim(self.min_int * .8, self.max_int * 1.15)
        else:
            self.axis.set_xlim(0, 1)
            self.axis.set_ylim(0, 1)

    def draw_plot(self):
        self.fig.canvas.restore_region(self.bg)
        for i, p in enumerate(self.plots):
            values = self.plot_vals[i]
            x = values[1]
            y = values[0][:len(x)]
            p[0].set_ydata(y)
            p[0].set_xdata(x)
            self.axis.draw_artist(p[0])
        self.graph.blit(self.fig.bbox)
        self.fig.canvas.flush_events()



    def update_val(self, ind, pixels):
        avg_val = n = 0
        corners = self.rects[ind]
        for x in range(corners.x1, corners.x2, 6):
            for y in range(corners.y1, corners.y2, 6):
                avg_val += sum(pixels[x][y])
                n += 1
        avg_val = avg_val / n

        if avg_val > self.max_int:
            self.max_int = avg_val
        if avg_val < self.min_int:
            self.min_int = avg_val

        now = datetime.datetime.now()

        box_vals = self.plot_vals[ind][0]
        time_vals = self.plot_vals[ind][1]

        box_vals.append(avg_val)
        time_vals.append(now)

        if(len(self.plot_vals[ind][0]) > 400):
            self.plot_vals[ind][0] = resize_list(box_vals)
            self.plot_vals[ind][1] = resize_list(time_vals)
            print("RESIZE")

    def update_vals(self, pixels):
        for i in range(len(self.rects)):
            self.update_val(i, pixels)
        self.update_plot()

    def del_self(self):
        self.graph.get_tk_widget().forget()
        plt.close('all')
