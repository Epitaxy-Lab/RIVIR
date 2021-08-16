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
    '''
    Return coordinate variables from a 2x2 point array

    @param coords: an input array of the form [[x,y],[x,y]]
    @return: x1, x2, y1, y2 points corresponding to corners of a rectangle.
    '''
    x1 = min(coords[0][0], coords[1][0])
    x2 = max(coords[0][0], coords[1][0])
    y1 = min(coords[0][1], coords[1][1])
    y2 = max(coords[0][1], coords[1][1])
    return x1, x2, y1, y2

def resize_list(list):
    '''
    Delete every other entry of the first half of a list, to better optimize plotting performance.

    @param list: list of points you would like to resize.
    @return: resized version of the list.
    '''
    half_length = int(len(list) / 2)
    first_half = list[:half_length]
    first_half_split = first_half[::2]

    return first_half_split + list[half_length:]

class coord():
    '''
    Object to store coordinate points.
    '''
    def __init__(self, rect):
        self.x1, self.x2, self.y1, self.y2 = assign_points(rect)

class plot_obj():
    '''
    Live plotting object to create an animated plot and update it. Plots intensity of pixels in a RHEED image.
    '''
    def __init__(self, rect_coords, canvas, color):
        '''
        Initializes a plot object, and sets up axis to update over.

        @param rect_coords: coordinate array corresponding to the corners of a rectangle on the image. Takes the form [[x,y],[x,y]]
        @param canvas: GUI canvas you would like to plot on.
        @param color: color of the line you would like to plot (should match drawn rectangle color).
        '''
        self.fig = plt.Figure(frameon=False)
        self.fig.autofmt_xdate()
        self.axis = self.fig.add_subplot(111)
        self.fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        #self.axis.axis("off")
        #self.axis.set_facecolor("#e3f2fd")
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
        '''
        Adds a new line to plot.

        @param rect_coords: rectangle coordinate array of the new area to plot.
        @param color: color of the new line.
        '''
        self.rects.append(coord(rect_coords))
        self.plot_vals.append([[],[]])
        self.plots.append(self.axis.plot_date([], [], linestyle='-', marker=',', animated=True, color=color))

    def del_line(self, ind):
        '''
        Delete a plotted line and stop tracking its data.

        @param ind: index of the line you would like to delete.
        '''
        del self.rects[ind]
        del self.plot_vals[ind]
        del self.plots[ind]
        return len(self.rects)

    def clear(self):
        '''
        Clear the entire plot and stop tracking values.
        '''
        new_vals = []
        for i in self.plot_vals:
            new_vals.append([[],[]])
        self.plot_vals = new_vals

    def update_plot(self):
        '''
        Update axis values of the current plot.
        '''
        self.axis.set_xlim(left=0, right=self.plot_vals[0][0][-1])
        longest_time = self.plot_vals[0][1]
        if(len(longest_time) > 1):
            self.axis.set_xlim(longest_time[0], longest_time[-1])
            self.axis.set_ylim(self.min_int * .8, self.max_int * 1.15)
        else:
            self.axis.set_xlim(0, 1)
            self.axis.set_ylim(0, 1)

    def draw_plot(self):
        '''
        Update the animation of the plot with the latest data. Uses blitting.
        '''
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
        '''
        Using the coordinates of the line, acquire the latest value of the pixel intensities in the coordinate box.

        @param ind: index corresponding to the rectangle area you would like to analyze.
        @param pixels: pixel array containing the values you would like to analyze.
        '''
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
        '''
        Update the values of all lines on the plot.
        '''
        for i in range(len(self.rects)):
            self.update_val(i, pixels)
        self.update_plot()

    def del_self(self):
        '''
        Delete the current plot.
        '''
        self.graph.get_tk_widget().forget()
        plt.close('all')
