#!/usr/bin/python3
import numpy as np
import cv2
import time
import sys
import math #TEMP!!!
import importlib
import imufusion

from threading import Thread
from queue import Queue
import AprilTagSubprocess
import DriverCameraSubprocess
import WebCameraSubprocess
import NetworkTablesSubprocess
import Pointcloudtransform
import PiecefindingSubprocess
import ArduinoSubprocess
import WebsocketSubprocess
import TableSubprocess
import BallsSubprocess
import Coprocess

import subprocess

azname = "Microsoft Corp. 4-Port USB 3.0 Hub"
loop = 0
while True:
    cmd = ['lsusb']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = proc.communicate()
    if azname in o.decode('ascii'):
        break
    else:
        sys.stdout.write("\033[F\033[K")
        print("Waiting" + "." * loop)
        if loop == 3:
            loop = 0
        else:
            loop += 1
        time.sleep(3)

import pyk4a
from pyk4a import Config, PyK4A
k4a = PyK4A(
    Config(
        camera_fps=pyk4a.FPS.FPS_30,
        color_resolution=0,
        depth_mode=pyk4a.DepthMode.WFOV_2X2BINNED,
        synchronized_images_only=False,
    )
)

global fovmode
fovmode = "WFOV"
global desiredfovmode
desiredfovmode = "WFOV"

k4a.start()

Coprocessthreads = 2
CoQueueIn = Queue()
for cp in range(0, Coprocessthreads):
    Thread(target=Coprocess.Process, args=(CoQueueIn,)).start()

TableQueue = Queue()
TableProcess = Thread(target=TableSubprocess.Process, args=(TableQueue, ))
TableProcess.start()

TagQueueIn = Queue()
TagQueueOut = Queue()
TagProcess = Thread(target=AprilTagSubprocess.Process, args=(TagQueueIn, TagQueueOut, TableQueue,))
TagProcess.start()

NTQueueIn = Queue()
NetworkTablesProcess = Thread(target=NetworkTablesSubprocess.Process, args=(NTQueueIn, TableQueue, ))
NetworkTablesProcess.start()

PCTQueueIn = Queue()
PCTQueueOut = Queue()
PCTProcess = Thread(target=Pointcloudtransform.Process, args=(PCTQueueIn, PCTQueueOut, CoQueueIn,))
PCTProcess.start()

#PCTQueueIn = Queue()
BallsQueueOut = Queue()
BallsProcess = Thread(target=BallsSubprocess.Process, args=(PCTQueueOut, BallsQueueOut,))
BallsProcess.start()

#PieceQueueIn = Queue()
PieceQueueOut = Queue()
PieceProcess = Thread(target=PiecefindingSubprocess.Process, args=(PCTQueueOut, PieceQueueOut, CoQueueIn,))
#PieceProcess.start()

CamQueueIn = Queue()
CamQueueOut = Queue()
CamProcess = Thread(target=DriverCameraSubprocess.Process, args=(CamQueueIn, CamQueueOut,))
#CamProcess.start()

#WebCamQueue = Queue()
WebCamProcess = Thread(target=WebCameraSubprocess.Process, args=(CamQueueOut,))
#WebCamProcess.start()

ArduinoQueue = Queue()
ArduinoProcess = Thread(target=ArduinoSubprocess.Process, args=(ArduinoQueue, NTQueueIn,))
#ArduinoProcess.start()

WebsocketProcess = Thread(target=WebsocketSubprocess.Process, args=(TableQueue,))
WebsocketProcess.start()

global prevfps
prevfps = [0, 0, 0, 0, 0]
global opti_prevfps
opti_prevfps = [0, 0, 0, 0, 0]
global prev_frame_time
prev_frame_time = 0
global cfg
cfg = []

global pos
pos = [4, 4, 0.85]
global localpos
localpos = [0, 0, 0]
global rot
rot = 0
while True:
    #print(k4a)
    try:
        frames = k4a.get_capture(3000)
    except:
        while True:
            cmd = ['lsusb']
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            o, e = proc.communicate()
            if azname in o.decode('ascii'):
                break
            else:
                sys.stdout.write("\033[F\033[K")
                print("Waiting" + "." * loop)
                if loop == 3:
                    loop = 0
                else:
                    loop += 1
                time.sleep(3)

        k4a = PyK4A(
            Config(
                camera_fps=pyk4a.FPS.FPS_30,
                color_resolution=0,
                depth_mode=pyk4a.DepthMode.WFOV_2X2BINNED,
                synchronized_images_only=False,
            )
        )

        fovmode = "WFOV"
        desiredfovmode = "WFOV"

        k4a.start()

        frames = k4a.get_capture(3000)
    depth = frames.depth
    sample = k4a.get_imu_sample()
    #color = frames.transformed_color
    opti_prev_frame_time = time.time()
    ir = frames.ir
    pt = frames.depth_point_cloud

    TagQueueIn.put([ir, pt, depth, fovmode])
    tagout = TagQueueOut.get(2)
    if len(tagout) > 1:
        #print("\033[1A\033[K\033[1A\033[K\033[1A\033[K\033[1A\033[K", end="")
        print("Pos: " + str(tagout[1]))
        pos = tagout[1]
        print("Rot: " + str(round(tagout[2], 2)))
        rot = tagout[2]
        dst = tagout[3]
        #print(dst)
        #if dst <= 2000:
        #    desiredfovmode = "WFOV"
        #elif dst >= 2000:
        #    desiredfovmode = "NFOV"
        #print(str(tagout[3] / 1000) + " M")
        NTQueueIn.put([pos, rot, tagout[4]])
        TableQueue.put([True, "Position", pos])
        TableQueue.put([True, "Yaw", rot])
    #else:
    #    print("\033[1A\033[K\033[1A\033[K", end="")
    PCTQueueIn.put([pt, pos, rot, sample])
    cv2.imshow("TagProcess", tagout[0])
    cv2.imshow("Pointcloudtransform", BallsQueueOut.get()[0])

    new_frame_time = time.time()
    fps = 1/((new_frame_time - prev_frame_time))
    prevfps = [prevfps[1], prevfps[2], prevfps[3], prevfps[4], fps]
    fps = round(sum(prevfps)/len(prevfps))
    prev_frame_time = new_frame_time
    print("FPS: " + str(fps),end="\n")

    opti_fps = 1/((new_frame_time - opti_prev_frame_time))
    opti_prevfps = [opti_prevfps[1], opti_prevfps[2], opti_prevfps[3], opti_prevfps[4], opti_fps]
    opti_fps = round(sum(opti_prevfps)/len(opti_prevfps))
    print("Optimal FPS: " + str(opti_fps),end="\n")

    waitKey = cv2.waitKey(delay=1)

    if waitKey == ord('q'):
        break
    elif waitKey == ord('m'):
        if desiredfovmode == "NFOV":
            desiredfovmode = "WFOV"
        else:
            desiredfovmode = "NFOV"
    elif waitKey == ord('n'):
        if desiredfovmode == "EWFOV":
            desiredfovmode = "ENFOV"
        else:
            desiredfovmode = "EWFOV"
    elif waitKey == ord('r'):
        TagQueueIn.put(None)
        TagProcess.join()
        importlib.reload(AprilTagSubprocess)
        TagProcess = Thread(target=AprilTagSubprocess.Process, args=(TagQueueIn, TagQueueOut, TableQueue,))
        TagProcess.start()
        print("here!")
    if desiredfovmode != fovmode:
        k4a._stop_cameras()
        k4a._stop_imu()
        if desiredfovmode == "NFOV":
            k4aconfig = Config(
                camera_fps=pyk4a.FPS.FPS_30,
                color_resolution=0,
                depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
                synchronized_images_only=False,
                )
            fovmode = "NFOV"
        elif desiredfovmode == "WFOV":
            k4aconfig = Config(
                camera_fps=pyk4a.FPS.FPS_30,
                color_resolution=0,
                depth_mode=pyk4a.DepthMode.WFOV_2X2BINNED,
                synchronized_images_only=False,
                )
            fovmode = "WFOV"
        elif desiredfovmode == "EWFOV":
            k4aconfig = Config(
                camera_fps=pyk4a.FPS.FPS_15,
                color_resolution=0,
                depth_mode=pyk4a.DepthMode.WFOV_UNBINNED,
                synchronized_images_only=False,
                )
            fovmode = "EWFOV"
        elif desiredfovmode == "ENFOV":
            k4aconfig = Config(
                camera_fps=pyk4a.FPS.FPS_30,
                color_resolution=0,
                depth_mode=pyk4a.DepthMode.NFOV_2X2BINNED,
                synchronized_images_only=False,
                )
            fovmode = "ENFOV"
        k4a.set_config(k4aconfig)
        k4a._start_cameras()
        k4a._start_imu()
TableQueue.put(None)
TagQueueIn.put(None)
PCTQueueIn.put(None)
PCTQueueOut.put(None)
NTQueueIn.put(None)
CamQueueOut.put(None)
TableProcess.join()
TagProcess.join()
NetworkTablesProcess.join()
print("Here")
WebCamProcess.join()
print("Here")
WebsocketProcess.join()
print("Here")
for cp in range(0, Coprocessthreads):
    CoQueueIn.put(None)
k4a.stop()

sys.exit(0)
