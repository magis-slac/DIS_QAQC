import os
import shutil
from pathlib import Path
import datetime
import argparse
import json
import PySpin

from pprint import pprint



def create_dir(p):
    if not Path(p).exists():
        Path(p).mkdir(parents=True, exist_ok=True)

def configure_cam(cam, config_dict):
    for k, v in config_dict.items():
        if not k in dir(cam):
            continue
        vprint(f"Configuring {k}:", eval(f"cam.{k}").ToString(), end='')
        eval(f"cam.{k}.SetValue({v})")
        vprint(" ->", eval(f"cam.{k}").ToString())

def get_image(cam):
    img = cam.GetNextImage()
    if img.IsIncomplete():
        print(f"Image is incomplete, with status {img.GetImageStatus()}")
        print("Continuing without saving the image...")
        return
    return img

def end_program():
    globals()["cam"].DeInit()
    del globals()["cam"]
    globals()["cam_list"].Clear()
    del globals()["cam_list"]
    globals()["system"].ReleaseInstance()
    del globals()["system"]

def main(args):
    global system
    system = PySpin.System.GetInstance()

    global cam_list
    cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()
    global cam
    if num_cameras > 1:
        print("Warning! More than one camera was found!")

        if a.verbose:
            vprint("List of cameras found:")
            for i in range(num_cameras):
                cam = cam_list.GetByIndex(i)
                cam.Init()
                vprint(f"Index {args.camera_index}, DeviceID {cam.DeviceID.GetValue()}")
                cam.DeInit()
                del cam

    cam = cam_list.GetByIndex(a.camera_index)
    cam.Init()
    print(f"The rest of the script will be run with camera of Index {args.camera_index} and DeviceID {cam.DeviceID.GetValue()}")

    print('=' * 80)

    print("Opening config file...")
    with open(args.config, 'r') as f:
        config = json.load(f)
    pprint(config)
    print(f"Successfully opened config file: {args.config}")
    config_name = Path(args.config).parts[-1].split('.')[0]
    time_str = datetime.datetime.now().strftime("%Y%m%d-%HH%MM%SS")
    dir_path = f"/data/DIS_QAQC/{config_name}_{time_str}"
    create_dir(dir_path)
    shutil.copy(args.config, dir_path)
    print('-' * 80)

    print("Applying \"Global\" config to the camera...")
    configure_cam(cam, config["Global"])
    print("Global configuration complete!")
    print('-' * 80)

    if not args.setup_only:
        cam.BeginAcquisition()

    for test_name in config.keys():
        if not "NumImages" in list(config[test_name].keys()):
            continue

        print(f"Applying {test_name} config to the camera...")
        configure_cam(cam, config[test_name])
        print(f"{test_name} configuration complete!")

        if args.setup_only:
            print('-' * 80)
            continue

        create_dir(f"{dir_path}/{test_name}")
        for i in range(config[test_name]["NumImages"]):
            print(f"Acquiring image {i+1}...")
            img = cam.GetNextImage()

            if img.IsIncomplete():
                print(f"Image {i+1} is incomplete! Status: {image_result.GetImageStatus()}")

            file_name = f"{dir_path}/{test_name}/img_{i+1}.raw"
            img.Save(file_name)
            print(f"Image saved at {file_name}!")

            img.Release()

        print('-' * 80)

    if not args.setup_only:
        cam.EndAcquisition()


    print("Ending script!")
    end_program()
    print('=' * 80)



if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    parser.add_argument('-c', '--config',
                        type=str)
    parser.add_argument('-s', '--setup_only',
                        action='store_true')
    parser.add_argument('--camera_index',
                        help="Specify which camera to test using index. Default: 0",
                        nargs='?', type=int, default=0)

    a = parser.parse_args()

    vprint = print if a.verbose else lambda *args, **kwargs: None

    vprint(a)

    main(a)
