from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import ocv, cv2, matplotlib
import matplotlib.pyplot as plt
import gui_plot, line_plot
import datetime
#from time import strftime
from camera import *

debug = False

### Initialize Variables
if(debug == False):
    camera, converter = ocv.initialize()

corner1 = corner2 = curr_rect = None
curr_rects = []
rect_plots = []
drag = False

img_size = (400, 500)
box_color = 'green'
###

def update_image():
    # Update graph with current image frame
    img_arr = grab_image(camera, converter)

    if(img_arr is not None):
        im = cv2.imencode(".png", cv2.cvtColor(img_arr, cv2.COLOR_BGR2HSV))[1].tobytes()
        graph_obj.draw_image(data=im, location=(0,600))
        #
        return img_arr

def webcam():
    ret, frame = cap.read()
    #img_arr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("test.png", frame)
    graph_obj.draw_image("test.png", location=(0, 600))
    return frame

def check_click():
    # Click and Drag functionality
    if event == "graf":
        x, y = values["graf"]
        click_and_drag(x, y)
    elif event.endswith('+UP'):
        save_rect()

def click_and_drag(x, y):
    global drag, corner1, corner2, curr_rect
    # First click check
    if not drag:
        corner1 = (x, y)
        drag = True
    else:
        corner2 = (x, y)

    # Delete old rectangle and draw
    if curr_rect:
        graph_obj.delete_figure(curr_rect)
    if None not in (corner1, corner2):
        curr_rect = graph_obj.draw_rectangle(corner1, corner2, line_color=box_color)

def save_rect():
    # Called upon mouse release
    global corner1, corner2, curr_rects, drag, num_plots, window, graph_obj
    if(corner1 is not None and corner2 is not None):
        rect = (corner1, corner2)
        curr_rects.append(rect)
        num_plots += 1
        new_window, graph_obj = redraw_lines(rect, rect_plots, num_plots)
        old_window = window
        window = new_window
        #old_window.close()
        rect_plots.append(line_plot.intensity_plot(rect, window['plot'+str(num_plots-1)].TKCanvas))
    corner1, corner2 = None, None
    drag = False

def check_plot(pixels):
    # Plot selection
    global curr_rects
    if len(curr_rects) > 0:
        rect = curr_rects[0]
        x1, y1 = rect[0]
        x2, y2 = rect[1]
        avg_val = 0
        n = 0
        for x in range(min(x1,x2), max(x1,x2)):
            for y in range(min(y1, y2), max(y1, y2)):
                avg_val += sum(pixels[x][y])
                n += 1
        avg_val = avg_val / n
        return avg_val

def update_plot(canvas):
    global fig, rect_plot
    fig_canv = FigureCanvasTkAgg(fig, canvas)
    fig_canv.get_tk_widget().forget()
    plt.close('all')
    r = rect_plot[0]
    ## plot_obj(r, window['canvas'].TKCanvas))
    f = matplotlib.figure.Figure(figsize=(6,5), dpi=100)
    plt.plot(r[0], r[1])
    f_agg = FigureCanvasTkAgg(f, canvas)
    f_agg.draw()
    f_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

def redraw_lines(rect, rect_plots, np):
    new_window = sg.Window("RHEED Viewing Software", create_layout(np), location=(0, 0), finalize=True)
    graph_obj = new_window['graf']

    for i, plot in enumerate(rect_plots):
        plot.update_canvas(new_window['plot'+str(i)].TKCanvas)

    return (new_window, graph_obj)

### Set up GUI window
sg.theme("Material1")

# def create_layout():
#     layout = [
#         [sg.Text("RIVIR",
#                 size=(15, 1),
#                 font=("Courier, 72"),
#                 justification="center")],
#         [sg.Text(" - Rheed Image VIeweR - ",
#                 size=(40, 1),
#                 font=("Courier, 28"),
#                 justification="center")],
#         [sg.Graph(canvas_size=img_size,
#                 graph_bottom_left=(0, 0),
#                 graph_top_right=img_size,
#                 key="graf",
#                 change_submits=True,
#                 drag_submits=True),
#
#         sg.Column[
#             [sg.Graph(canvas_size=)]
#         ]
#
#         [sg.Text("Bottom", size=(14, 1))]
#         #[sg.Image(filename="", key="imgfeed")]
#     ]

def create_layout(num_plots):
    graphs_part = [sg.Graph(canvas_size=(700, 100),
        graph_bottom_left=(0, 0),
        graph_top_right=(700, 100),
        key=f"plot{i}") for i in range(num_plots)]
    print(graphs_part)
    layout = [
        [sg.Text("RIVIR",
                size=(15, 1),
                font=("Courier, 72"),
                justification="center")],

        [sg.Text(" - Rheed Image VIeweR - ",
                size=(40, 1),
                font=("Courier, 28"),
                justification="center")],

        [sg.Graph(canvas_size=img_size,
                graph_bottom_left=(0, 0),
                graph_top_right=img_size,
                key="graf",
                change_submits=True,
                drag_submits=True), sg.Column([graphs_part])],

        [sg.Text("Bottom", size=(14, 1))]
        #[sg.Image(filename="", key="imgfeed")]
    ]
    return layout
###

# Create the window
num_plots = 0
update_window = False
window = sg.Window("RHEED Viewing Software", create_layout(num_plots), location=(0, 0), finalize=True)#, location=(800,400))
graph_obj = window["graf"]


if(debug):
    cap = cv2.VideoCapture(0)

### EVENT LOOP ###
while True:
    event, values = window.read(timeout=1)
    if event == "OK" or event == sg.WIN_CLOSED:
        break

    img_array = webcam() if debug else update_image()
    check_click()

    for rect in curr_rects:
        graph_obj.draw_rectangle(rect[0], rect[1], line_color=box_color)

    if img_array is not None:
        for plot in rect_plots:
            plot.update_vals(img_array)

if(debug == False):
    print("Closing Camera Connection...")
    free_camera(camera)
print("Exiting program.")
window.close()
