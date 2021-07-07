from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import ocv, cv2, matplotlib
import matplotlib.pyplot as plt
import gui_plot
import datetime
import threading
import time
from camera import *

def update_image():
    # Update graph with current image frame
    img_arr = grab_image(camera, converter)

    if(img_arr is not None):
        img_arr_gs = cv2.resize(img_arr, img_size)
        #img_arr_cm = cv2.cvtColor(img_arr, cv2.COLOR_BGR2HSV)
        img_arr_cm = cv2.cvtColor(img_arr, cv2.COLOR_BGR2Luv)
        cv2.imwrite("rheed.png", img_arr_cm)
        graph_obj.draw_image("rheed.png", location=(0,600))
        #im = cv2.imencode(".png", img_arr)[1].tobytes()
        return img_arr_gs

def update_plots(plotter, image_arr, num):
    plotter.update_vals(image_arr)
    time.sleep(.1)
    window.write_event_value("THREAD_FIN", num)

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
        curr_rect = graph_obj.draw_rectangle(corner1, corner2, line_color='red')

def save_rect():
    # Called upon mouse release
    global corner1, corner2, curr_rects, drag
    if(corner1 is not None and corner2 is not None):
        rect = (corner1, corner2)
        curr_rects.append(rect)
        rect_plots.append(gui_plot.plot_obj(rect, window['plot'].TKCanvas))
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


if __name__ == "__main__":
    ### Initialize Variables
    camera, converter = ocv.initialize()

    corner1 = corner2 = curr_rect = None
    curr_rects = []
    rect_plots = []
    drag = False

    img_size = (500, 600)

    fig = matplotlib.figure.Figure(figsize=(2,1), dpi=10)
    fig.add_subplot(111).plot([], [])
    ###

    ### Set up GUI window
    sg.theme("Material1")

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
                drag_submits=True),

        sg.Canvas(key="plot")]
        #[sg.Image(filename="", key="imgfeed")]
    ]
    ###

    # Create the window
    window = sg.Window("RHEED Viewing Software", layout, location=(0, 0), finalize=True)#, location=(800,400))
    graph_obj = window["graf"]


    ### EVENT LOOP ###
    while True:
        event, values = window.read(timeout=1)
        if event is None:
            break

        if event == "THREAD_FIN":
            rect_plots[values[event]].draw_plot()


        img_array = update_image()
        check_click()

        for rect in curr_rects:
            graph_obj.draw_rectangle(rect[0], rect[1], line_color='red')

        if img_array is not None and len(rect_plots) > 0:
            #result = multiprocess.Pool().map(update_plots, zip(rect_plots, [img_array*len(rect_plots)]));
            for (i, plot) in enumerate(rect_plots):
                threading.Thread(target=update_plots, args=[plot, img_array, i], daemon=True).start()
                #print(Queue().get())
                #plot.update_vals(img_array)
                #window.write_event_value("-THREAD_", "Done.")

    print("Closing Camera Connection...")
    free_camera(camera)
    print("Exiting program.")
    window.close()
