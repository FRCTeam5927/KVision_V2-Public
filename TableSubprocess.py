import json

def Process(q):
    global Table
    try:
        tablebackup = open("table.json", "r")
        Table = json.load(tablebackup)
        tablebackup.close()
    except:
        Table = {"Position":[0, 0, 0], "Yaw":0, "Tag8":True, "Tag7":True, "Tag6":True, "Tag5":True, "Tag4":True, "Tag3":True, "Tag2":True, "Tag1":True, "Multipoint Samples":35, "Z Min":-0.35, "Z Max":-0.05, "Arm Offset":0.0, "UpdateGyroArm":False, "gets":0, "Fast Inverse Light Falloff":False}
    while True:
        QueueIn = q.get()
        if QueueIn == None:
            tablebackup = open("table.json", "w")
            json.dump(Table, tablebackup, indent = 4)
            break
        putmode = QueueIn[0]
        varname = QueueIn[1]
        if putmode:
            varvalue = QueueIn[2]
            Table[varname] = varvalue
        else:
            Table["gets"] += 1
            ReturnQueue = QueueIn[2]
            if varname == "*":
                ReturnQueue.put(Table)
            elif varname in Table:
                ReturnQueue.put(Table[varname])
            else:
                ReturnQueue.put(0)
        #print(Table)
