import PySpin

system = PySpin.System.GetInstance()

cam_list = system.GetCameras()

cam = cam_list.GetByIndex(0)
cam.Init()

node_map = cam.GetNodeMap()
# print(node_map)
nodes = node_map.GetNodes()
# print(nodes)

# for node in nodes:
#     print(node.GetName())

for prop in dir(cam):
    try:
        t = type(eval(f"cam.{prop}"))
        val = eval(f"cam.{prop}").ToString()
        print(f"{prop}: {val}")
    except:
        t = type(eval(f"cam.{prop}"))
        # print(f"{prop}: {val}")
        print(f"{prop}: {t}, exception occured!")

cam.DeInit()
del cam
cam_list.Clear()
system.ReleaseInstance()
