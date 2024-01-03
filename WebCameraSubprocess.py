import time
import cv2
from mjpeg_streamer import MjpegServer, Stream
import numpy as np
#import setproctitle
def Process(q):
    #setproctitle.setproctitle("WebCamProcess")
    stream = Stream("my_camera", size=(512, 106), quality=50, fps=30)
    server = MjpegServer("0.0.0.0", 8080)
    server.add_stream(stream)
    server.start()

    while True:
        QueueIn = q.get()
        if q.get() == None:
            try:
                server.stop()
            except:
                break
        stream.set_frame(QueueIn[0])#np.full((512, 424, 3), 255, np.uint8))
