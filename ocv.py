'''
Python code utilizing OpenCV for display of Pylon-compatible camera.

@author: Adam_Abbas
'''
import cv2, time
from camera import *

def initialize():
    '''
    Initialize relevant camera variables.

    @param none
    @return: a tuple containing the relevant InstantCamera and ImageFormatConverter
    '''
    cam = init_cam_w_video()
    conv = init_OCV_converter()

    return (cam, conv)

def display_image(image):
    '''
    Display a Pylon image array using OpenCV.

    @param image: an OpenCV compatible Pylon image array.
    @return: None
    '''
    cv2.namedWindow('RHEED Viewer', cv2.WINDOW_NORMAL)
    cv2.imshow('title', image)

def take_input():
    '''
    Input management for default OpenCV GUI.
    @param None
    @return: an integer representing the outcome. 0 if no key was pressed, 1 if an image was saved, and -1 if the window has been quit
    '''
    k = cv2.waitKey(10)
    if k == ord(' '):
        cv.imwrite("name", image)
        return 1
    if k == ord('x'):
        return -1
    return 0

def close_cv():
    '''
    Destroys all OpenCV windows, ending the livestream.

    @param None
    @return None
    '''
    cv2.destroyAllWindows()

def run():
    '''
    Main executable loop for OpenCV Pylon visualization. Continues to execute until exit key is pressed.

    @param None
    @return: None
    '''
    camera, converter = initialize()
    inp = 0

    while(inp != -1):
        img_arr = grab_image(camera, converter)
        if(img_arr is not None):
            display_image(img_arr)
        inp = take_input()
        statement = "Saving image." if inp == 1 else "Exiting Program."
        if inp != 0:
            print(statement);
    free_camera(camera)
    close_cv()
    print("Exiting successful.")



#run()
