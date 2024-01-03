import numpy as np
import cv2
import setproctitle
def Process(q, o):
    setproctitle.setproctitle("CamProcess")

    multiplymask = []
    multiplymaskpass = 0
    while not len(multiplymask) == 424:
        if multiplymaskpass == 0:
            multiplymask.append(np.full((512), 1))
        else:
            multiplymask.append(np.full((512), 4**multiplymaskpass))
        if multiplymaskpass == 3:
            multiplymaskpass = 0
        else:
            multiplymaskpass += 1
    multiplymask = np.uint8(multiplymask)

    while True:
        QueueIn = q.get()
        depthimg = QueueIn[0]

        depthimg = cv2.medianBlur(depthimg, 5)
        #c = cv2.divide(255, cv2.inRange(depthimg, 100, 750))
        #m = cv2.divide(512, cv2.inRange(depthimg, 750, 3000))
        #f = cv2.divide(765, cv2.inRange(depthimg, 3000, 5000))

        #outimg = cv2.add(c, cv2.add(m, f))
        #outimg = cv2.multiply(np.uint8(outimg), np.uint8(multiplymask))
        #s1, s2, s3, s4 = outimg[0::4], outimg[1::4], outimg[2::4], outimg[3::4]
        #outimg = cv2.add(s1, cv2.add(s2, cv2.add(s3, s4)))\

        outimg = cv2.merge((cv2.inRange(depthimg, 3000, 5000), cv2.inRange(depthimg, 750, 3000), cv2.inRange(depthimg, 100, 1500)))
        #outimg = np.uint8(cv2.inRange(depthimg, 3000, 5000)/255+cv2.inRange(depthimg, 750, 3000)/255*2)*4*4

        #sobelx = cv2.Sobel(depthimg, cv2.CV_32F, 0, 1)
        #sobely = cv2.Sobel(depthimg, cv2.CV_32F, 1, 0)
        #magnitude = cv2.sqrt(cv2.add(cv2.multiply(sobely, sobely), cv2.multiply(sobelx, sobelx)))
        #mask = cv2.bitwise_not(cv2.inRange(magnitude, 400, 10000))

        #os1 = cv2.bitwise_and(outimg, 3)
        #os2 = cv2.bitwise_and(outimg, 12) >> 2
        #os3 = cv2.bitwise_and(outimg, 48) >> 4
        #os4 = cv2.bitwise_and(outimg, 192) >> 6
        #outimg = np.ravel([os1, os2, os3, os4], 'F').reshape(512, 424).T
        #outimg = cv2.merge((cv2.inRange(outimg, 40, 50), cv2.inRange(outimg, 2, 3), cv2.inRange(outimg, 1, 2)))
        o.put([np.uint8(outimg)])
