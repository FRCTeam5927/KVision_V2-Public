import numpy as np
import cv2
import imufusion
from queue import Queue
import time
import PointMath3d
import math
def Process(q, o, cq):
    co = Queue()
    QueueIn = [0]
    framenum = 0
    while True:
        if framenum > 5:
            framenum = 0
        else:
            framenum += 0.01
        if q != None:
            QueueIn = q.get()

        if QueueIn == None:
            break

        pointimg = QueueIn[0] #Camera Space!

        #out = np.delete(out, np.where((out == [0,0,0]).all(axis=1)), axis=0)
        res = 30
        #out[np.abs(out[:, :, 1]) > 500] = [0, 0, 0]
        x, z, y = cv2.split(cv2.divide(pointimg, (res, res, res, 0)))
        #x = -x
        #ptmin = pointimg.min()
        xmin = 0
        ymin = 0
        #xmax = x.max()
        #ymax = y.max()
        #y = cv2.add(y, int(abs(ymin)))
        #x = cv2.add(x, int(abs(xmin)))
        #y = cv2.add(y, int(8100/2/res))
        #x = cv2.add(x, int(16500/2/res))
        #x[0 > x] = 0
        #x[x > int(16500/res)] = 0
        #y[y < -int(8100/res)] = 0
        #y[y > int(8100/res)] = 0
        BEV = np.zeros((int(8100/res), int(16500/res)), dtype=np.uint8)
        #BEV = np.zeros((ymax-ymin+1, xmax-xmin+1), dtype=np.uint8)
        BEV[y.flatten(), -x.flatten()] = 255

        contours, hierarchy = cv2.findContours(BEV, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #contours = []
        newcontours = []
        cbounds = []
        for c in contours:
            area = cv2.contourArea(c)
            if 3000/res > area > 300/res:
                #c = cv2.boundingRect(c)
                x,y,w,h = cv2.boundingRect(c)
                ratio = w/h
                if 0.5 < ratio < 2:
                    w = ((x+w)-abs(xmin))*res/1000
                    x = (x-abs(xmin))*res/1000
                    h = ((y+h)-abs(ymin))*res/1000
                    y = (y-abs(ymin))*res/1000
                    cbounds.append([(y, -w, -10), (h, -x, 10)])
                    rect = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect)
                    A, B, C, D = box
                    AB = math.sqrt((A[1] - B[1])**2 + (A[0] - B[0])**2)
                    BC = math.sqrt((B[1] - C[1])**2 + (B[0] - C[0])**2)
                    CD = math.sqrt((C[1] - D[1])**2 + (C[0] - D[0])**2)
                    DA = math.sqrt((D[1] - A[1])**2 + (D[0] - A[0])**2)
                    boxlen = [AB, BC, CD, DA]
                    if 250*(2/3)/res < max(boxlen) < 250/res and min(boxlen) > 250/3/res:
                        #print("c")
                        #print(AB)
                        c = np.int0(box)
                        newcontours.append(c)
        #canvas = np.zeros((out.shape[0], out.shape[1]), dtype=np.uint8)
        if False:#len(newcontours) != 0:
            #color = q.get()
            #cbounds = [cbounds[1]]
            #newcontours = [newcontours[1]]
            oldtime = time.time()
            for b in cbounds:
                #m = cv2.inRange(out, (b[0][1] * 1000, b[1][2] * -1000, b[0][0] * 1000), (b[1][1] * 1000, b[0][2] * -1000, b[1][0] * 1000))
                cq.put([0, co, out, b])
            waitloop = 1
            while waitloop <= len(cbounds):
                m = co.get()#cv2.inRange(out, (b[0][1] * 1000, b[1][2] * -1000, b[0][0] * 1000), (b[1][1] * 1000, b[0][2] * -1000, b[1][0] * 1000))
                #print(meancolor)
                canvas = cv2.bitwise_or(canvas, m)
                waitloop += 1
            print(time.time() - oldtime)
            #if not color is None:
                #out = cv2.bitwise_and(color, color, mask=mask)
            #else:
                #out = mask
        BEV = cv2.drawContours(BEV, newcontours, -1, 128, 3)


        #print(out.flatten().reshape(-1, 3))
        #out = PointMath3d.point_cloud_2_birdseye(out.flatten().reshape(-1, 3))

        #y, z, x = cv2.split(out.astype(np.int16))
        #lgtarg = np.float32([1.0274299999999998, -1.071626, -0.46279])
        #lgtarg = lgtarg*1000

        #lgtarg = out[int(out.shape[1]/2), int(out.shape[0]/2)]
        #lgtarg = [-2000, 0, 0]
        #lgtarg = np.float32([0, -lgtarg[0], lgtarg[1]])

        #blank = np.zeros(x.shape, dtype=np.int16)
        #dst = 1/(((x+lgtarg[0])**2+(y-lgtarg[1])**2+(z-lgtarg[2])**2)/250000)
        #dst[dst > 1] = 1
        #dst = cv2.bitwise_and(dst, dst, mask=mask)
        #dst *= 255

        #dst = cv2.normalize(dst, None, 1, 0, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        #dst = cv2.inRange(dst, 0, 1000)
        o.put(BEV)
