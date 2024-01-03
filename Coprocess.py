import cv2
import numpy as np

def Process(q):
    while True:
        QueueIn = q.get()
        if QueueIn == None:
            break
        task = QueueIn[0]
        o = QueueIn[1]
        if task == 0:
            pt = QueueIn[2]
            b = QueueIn[3]

            m = cv2.inRange(pt, (b[0][1] * 1000, b[1][2] * -1000, b[0][0] * 1000), (b[1][1] * 1000, b[0][2] * -1000, b[1][0] * 1000))
            #canvas[m == 255] = cv2.mean(color, m)



            o.put(m)#cv2.mean(color, m))
        if task == 1:
            sept = QueueIn[2]
            rotmulti = QueueIn[3]

            x = cv2.multiply(sept[0], rotmulti[0])
            y = cv2.multiply(sept[1], rotmulti[1])
            z = cv2.multiply(sept[2], rotmulti[2])

            o.put(cv2.add(x, cv2.add(y, z)))
