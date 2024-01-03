import ntcore
import math
from queue import Queue
import time
def Process(q, tq):
    trq = Queue()
    inst = ntcore.NetworkTableInstance.getDefault()
    # get the subtable called "datatable"
    vint = inst.getTable("Vision")
    sdnt = inst.getTable("SmartDashboard")

    Position = vint.getFloatArrayTopic("Position").publish()
    Yaw = vint.getFloatTopic("Yaw").publish()
    QueueIn = [0]
    while True:
        if not q.empty():
            QueueIn = q.get()
            if QueueIn == None:
                break
            if True:#NetworkTables.isConnected():
                Position.set(QueueIn[0])
                Yaw.set(math.radians(QueueIn[1]))
                #vint.putNumber('Yaw', math.radians(QueueIn[1]))
                #debug.putNumber('YawDebug', QueueIn[1])
                #debug.putNumberArray('TagDebug', QueueIn[2])
                #debug.putNumber('Distence', QueueIn[2][3])
                #debug.putNumber('TagNum', QueueIn[2][4])
        #if NetworkTables.isConnected():
        #    tq.put([False, "Arm Offset", trq])
        #    tq.put([False, "UpdateGyroArm", trq])
        #    ArmOffset = trq.get()
        #    UpdateGyroArm = trq.get()
        #    if UpdateGyroArm == True:
        #        sdnt.putNumber('ArmOffset', -ArmOffset)
        #    sdnt.putBoolean('UpdateGyroArm', UpdateGyroArm)
        time.sleep(1/60)
