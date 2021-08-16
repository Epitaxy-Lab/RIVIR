'''
Python code to interface with cameras.

@author: Adam_Abbas
'''

from pypylon import pylon

def init_cam_w_video():
    '''
    Initialize a connection with the first available Basler gigE connected camera.
    Begins a continous video stream upon connecting.

    @param none
    @return: an InstantCamera object
    '''
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    print("Connection established with device: ", camera.GetDeviceInfo().GetModelName())

    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    return camera

def init_OCV_converter():
    '''
    Initialize a Pylon image converter to produce an openCV format.

    @param none
    @return: an ImageFormatConverter
    '''
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed

    return converter

def grab_image(cam, conv):
    '''
    Grab the live frame from the Basler camera object.

    @param cam: a live InstantCamera object
    @param conv: ImageFormatConverter to desired format
    @return: an openCV compatible Pylon image array.
    @raise OSError: grab unsuccessful
    @raise TimeoutError: camera exceeded timeout time
    '''
    grab = cam.RetrieveResult(10000, pylon.TimeoutHandling_ThrowException) #TODO: verify timeout

    # if not grab.GrabSucceeded():
    #      print(grab.ErrorCode)
    #      print(grab.ErrorDescription)
    #      #raise OSError("Grab failure.")

    if grab.GrabSucceeded():
        image = conv.Convert(grab)
        pixel_arr = image.GetArray()

        return pixel_arr
        
    grab.Release()
    return None

def free_camera(cam):
    '''
    Destroys input camera object, releasing associated resources.

    @param cam: a live InstantCamera object
    @return: None
    '''
    cam.StopGrabbing()
