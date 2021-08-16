
from pypylon import pylon

tlFactory = pylon.TlFactory.GetInstance()
devices = tlFactory.EnumerateDevices()
camera = pylon.InstantCameraArray(min(len(devices), 2))
for i, cam in enumerate(camera):
    cam.Attach(tlFactory.CreateDevice(devices[i]))
    print("Using device: ", cam.GetDeviceInfo().GetFriendlyName(), i)

camera = camera[0]
# demonstrate some feature access
new_width = camera.Width.GetValue() - camera.Width.GetInc()

if new_width >= camera.Width.GetMin():
    camera.Width.SetValue(new_width)

    numberOfImagesToGrab = 100
    camera.StartGrabbingMax(numberOfImagesToGrab)

    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Access the image data.
            print("SizeX: ", grabResult.Width)
            print("SizeY: ", grabResult.Height)
            img = grabResult.Array
            print("Gray value of first pixel: ", img[0, 0])

            grabResult.Release()
    camera.Close()
