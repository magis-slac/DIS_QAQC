import PySpin

system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
cam = cam_list.GetByIndex(0)

cam.Init()
cam.BeginAcquisition()
cam.EndAcquisition()
cam.DeInit()
cam.Init()
cam.DeInit()
del cam

cam_list.Clear()
del cam_list

system.ReleaseInstance()
