import numpy as np
import cv2
import math
def Process(q, o):
    while True:

        if q != None:
            QueueIn = q.get()

        if QueueIn == None:
            break
        pointimg = QueueIn[0] #Global Space!
        pointimg8 = np.uint8(pointimg)
        pointimggray = cv2.cvtColor(pointimg8, cv2.COLOR_RGB2GRAY)
        contours, hierarchy = cv2.findContours(pointimggray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(pointimg8, contours, -1, (0,255,0), 3)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 35:
                continue
            leftmost = tuple(contour[contour[:,:,0].argmin()][0])
            rightmost = tuple(contour[contour[:,:,0].argmax()][0])
            topmost = tuple(contour[contour[:,:,1].argmin()][0])
            bottommost = tuple(contour[contour[:,:,1].argmax()][0])
            leftpt = pointimg[leftmost[1], leftmost[0]]
            rightpt = pointimg[rightmost[1], rightmost[0]]
            toppt = pointimg[topmost[1], topmost[0]]
            bottompt = pointimg[bottommost[1], bottommost[0]]
            dsth = math.sqrt((leftpt[0]-rightpt[0])**2+(leftpt[2]-rightpt[2])**2)
            dstv = math.sqrt((toppt[1]-bottompt[1])**2+(toppt[2]-bottompt[2])**2)
            #if not 200 <= dsth <= 300:
            #    continue
            #print(math.sqrt((leftpt[0]-rightpt[0])**2+(leftpt[1]-rightpt[1])**2+(leftpt[2]-rightpt[2])**2))
            arclen = cv2.arcLength(contour, True)
            if arclen != 0:
                ratio = 4 * math.pi * area / (arclen * arclen)
            else:
                ratio = 1
            #if not ratio >= 0.60:
            #    continue
            #hull = cv2.convexHull(contour)
            #cv2.drawContours(pointimg8, [contour], -1, (0,255,0), 3)

            font = cv2.FONT_HERSHEY_SIMPLEX

            # fontScale
            fontScale = 0.5

            # Blue color in BGR
            color = (255, 0, 0)

            # Line thickness of 2 px
            thickness = 2

            # Using cv2.putText() method
            cv2.line(pointimg8, (leftmost[0], topmost[1]), (rightmost[0], topmost[1]), (255, 255, 255), 3)
            cv2.line(pointimg8, [leftmost[0], topmost[1]], [leftmost[0], bottommost[1]], (255, 255, 255), 3)
            cv2.putText(pointimg8, str(round(dsth)) + " mm", [leftmost[0], topmost[1]], font, fontScale, color, thickness, cv2.LINE_AA)
            cv2.putText(pointimg8, str(round(dstv)) + " mm", [leftmost[0], int((topmost[1]+bottommost[1])/2)], font, fontScale, color, thickness, cv2.LINE_AA)

            pointimg8 = cv2.putText(pointimg8, str(round(ratio, 2)), [rightmost[0], int((topmost[1]+bottommost[1])/2)], font,
                            fontScale, (0, 0, 255), thickness, cv2.LINE_AA)
        o.put([pointimg8])
