from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import ocv, cv2, matplotlib, random
import matplotlib.pyplot as plt
import gui_plot
import datetime
import threading
import datetime, os
from camera import *

### SET TO USE WEBCAM
debug = False

def update_image():
    # Update graph with current image frame
    img_arr = grab_image(camera, converter)

    if(img_arr is not None):
        conv = cv2.cvtColor(img_arr, cv2.COLOR_BGR2HSV)
        im = cv2.imencode(".png", conv)[1].tobytes()
        #img_arr_cm = cv2.cvtColor(img_arr, cv2.COLOR_BGR2Luv)
        graph_obj.draw_image(data=im, location=(0,600))
        #im = cv2.imencode(".png", img_arr)[1].tobytes()
        return conv

def webcam():
    ret, frame = cap.read()
    #img_arr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("test.png", frame)
    graph_obj.draw_image("test.png", location=(0, 600))
    return frame

def update_plots(plotter, image_arr, num):
    plotter.update_vals(image_arr)
    #time.sleep(.1)
    #window.write_event_value("THREAD_FIN", num)

def check_inp(event):
    # Click and Drag functionality
    if event == "graf":
        x, y = values["graf"]
        click_and_drag(x, y)
    elif event.endswith('+UP'):
        save_rect()
    elif event.isdigit():
        to_rm = int(event)-1
        if(to_rm >= len(curr_rects)):
            print("Rectangle index too high.")
            return
        del curr_rects[to_rm]
        return to_rm
    elif event == "Save Image":
        return -1
    elif event == "Clear Plot":
        return -2

def click_and_drag(x, y):
    global drag, corner1, corner2, curr_rect
    # First click check
    if not drag:
        corner1 = (x, y)
        drag = True
        graph_obj.draw_text(str(len(curr_rects)+1), corner1, font=("Arial", 64))
    else:
        corner2 = (x, y)

    # Delete old rectangle and draw
    if curr_rect:
        graph_obj.delete_figure(curr_rect)
    if None not in (corner1, corner2):
        draw_rect_pair(corner1, corner2, str(len(curr_rects)+1))

def draw_rect_pair(corner1, corner2, i, color="yellow"):
    curr_rect = graph_obj.draw_rectangle(corner1, corner2, line_color=color)
    graph_obj.draw_text(i, corner1, color="white", font=("Arial", 32))

def save_rect():
    # Called upon mouse release
    global corner1, corner2, curr_rects, drag, main_plot
    if(corner1 is not None and corner2 is not None):
        rect = (corner1, corner2)
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        curr_rects.append((rect, color))
        if main_plot is None:
            main_plot = gui_plot.plot_obj(rect, window['plot'].TKCanvas, color)
        else:
            main_plot.add_line(rect, color)
    corner1, corner2 = None, None
    drag = False

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

def thread_plot(plotter, img_arr):
    plotter.update_vals(img_arr)
    #plotter.draw_plot()


if __name__ == "__main__":
    ### Initialize Variables
    if(debug == False):
        camera, converter = ocv.initialize()

    corner1 = corner2 = curr_rect = None
    curr_rects = []
    main_plot = None
    drag = save_im = False

    img_size = (500, 600)

    ### Set up GUI window
    sg.theme("Material1")

    layout = [
        [sg.Text("RIVIR",
                size=(20, 1),
                font=("Courier, 72"),
                justification="center")],

        [sg.Text(" - Rheed Image VIeweR - ",
                size=(50, 1),
                font=("Courier, 28"),
                justification="center")],

        [sg.Graph(canvas_size=img_size,
                graph_bottom_left=(0, 0),
                graph_top_right=img_size,
                key="graf",
                change_submits=True,
                drag_submits=True),

        sg.Canvas(key="plot")],

        [sg.Button("Save Image", size=(20,1)),
        sg.Button("Clear Plot", size=(20,1))]
        #[sg.Image(filename="", key="imgfeed")]
    ]
    ###

    # Create the window
    window = sg.Window("RHEED Viewing Software", layout, location=(0, 0), return_keyboard_events=True, element_justification='c', finalize=True)#, location=(800,400))
    graph_obj = window["graf"]

    if(debug):
        cap = cv2.VideoCapture(0)

    if not os.path.isdir("data"):
        os.mkdir("data")

    ### EVENT LOOP ###
    while True:
        event, values = window.read(timeout=0)
        if event is None:
            break

        img_array = webcam() if debug else update_image()
        success = img_array is not None
        inp_ret = check_inp(event)

        if inp_ret is not None:
            if(inp_ret >= 0):
                num_rcts = main_plot.del_line(inp_ret)
                if(num_rcts == 0):
                    main_plot = main_plot.del_self()
            elif(inp_ret == -1):
                save_im = True
            elif(inp_ret == -2 and main_plot is not None):
                main_plot.clear()


        if save_im and success:
            filename = "data/%s" % datetime.datetime.now().strftime("RIVIR-%m%d_%H%M%S.jpg")
            print(filename)
            print(cv2.imwrite(filename, img_array))
            save_im = False

        r_count = 1
        for rect in curr_rects:
            draw_rect_pair(rect[0][0], rect[0][1], r_count, color=rect[1])
            r_count+=1

        if success and main_plot is not None:
            threading.Thread(target=thread_plot, args=(main_plot, img_array), daemon=True).start()
            #main_plot.update_vals(img_array)
            main_plot.draw_plot()

    if(debug == False):
        print("Closing Camera Connection...")
        free_camera(camera)
    else:
        cap.release()
    print("Exiting program.")
