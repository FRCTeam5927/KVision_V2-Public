import numpy as np
import cv2
import imufusion
from queue import Queue
import time
import PointMath3d
import math
def Process(q, o, cq):

    bounds = [
        #[(1.0274-0.25, 1.0716-0.25, 0.05), (1.0274+0.25, 1.0716+0.25, 1)]
        #[(0, 0, 0.05), (16.5, 8.01, 2)]
        [(-1, -1, 0.02), (1, 1, 2)]    #[(0, 0, 0), (1, 1, 1)]
        #[(-16.5, -8.01, -0.23), (0, 0, -0.1)]
        #[(0, 0, -10), (1, 1, 10)],
        #[(-10, -10, -10), (10, 10, -0.28)],
        #[(-10, -10, 0), (10, 10, 10)],
        #[(5, 5, -100), (100, 100, 100)],
        #[(-10, -10, -10), (30, 0, 10)]
        #[(-10, -10, -10), (10, 10, -.7)]
        ]
    ahrs = imufusion.Ahrs()
    global prev_timestamp
    prev_timestamp = 0
    global lgtarg
    lgtarg = [0, 0, 0]
    global lastrot
    lastrot = [0, 0]
    QueueIn = [0]
    framenum = 0
    cxo = Queue()
    cyo = Queue()
    czo = Queue()
    co = Queue()
    Queues = [cq, cxo, cyo, czo]
    #o.put([np.ones((255, 255, 3), dtype=np.int16)])
    temprot = 1
    while True:
        temprot += 1
        if q != None:
            QueueIn = q.get()

        if QueueIn == None:
            break

        pointimg = QueueIn[0] #Camera Space!
        pos = QueueIn[1] #Global Space!
        rot = 180-QueueIn[2]
        sample = QueueIn[3]

        timestamp = sample.pop("acc_timestamp")

        ahrs.update_no_magnetometer(np.degrees(np.float64(sample.pop("gyro_sample"))), np.float64(sample.pop("acc_sample")) * 9.80665, (timestamp-prev_timestamp)/1000000)
        samplerot = ahrs.quaternion.to_euler() #Roll, Pitch, Yaw
        samplerot[0] = 180-samplerot[0]
        samplerot[1] = samplerot[1]-6.5
        print(samplerot[0])
        samplerot[2] = 180-samplerot[2]

        if not rot == 0:
            lastrot = [rot, samplerot[2]]
        else:
            rot = lastrot[0] + (lastrot[1] - samplerot[2])
        #rot -= 90
        prev_timestamp = timestamp
        mask = cv2.inRange(pointimg, 0, 0)
        out = pointimg
        out = PointMath3d.rotatePoints3(out, [math.radians(-samplerot[0]), math.radians(-rot), math.radians(samplerot[1])], Queues)
        out = cv2.subtract(out, (pos[0]*1000, pos[2]*1000, pos[1]*1000, 0))

        for b in bounds:
            m = cv2.inRange(out, (b[1][0] * -1000, b[1][2] * -1000, b[1][1] * -1000), (b[0][0] * -1000, b[0][2] * -1000, b[0][1] * -1000))#(-1000, -1000, -1000), (1000, 1000, 1000))
        #    print(len(m[m != 0]) >= 25)
            mask = cv2.bitwise_or(mask, cv2.bitwise_not(m))
        mask = cv2.bitwise_not(mask)
        out = cv2.bitwise_and(out, out, mask=mask)
        o.put([out])
