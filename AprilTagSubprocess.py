import math
import json
from queue import Queue
import numpy as np
import cv2
import apriltag
import FieldGeometry
import PointMath3d
from multiprocessing import shared_memory

tagoptions = apriltag.DetectorOptions(families="tag16h5", nthreads=4, quad_decimate=0, refine_pose=False)
tagdetector = apriltag.Detector(tagoptions)

def az_TagToPointCloudPos(t, pt, mode = 0, weight = None, safe = False):
    if weight == None:
        tpos = [int(t.center[0]), int(t.center[1])]
    else:
        (ptA, ptB, ptC, ptD) = t.corners

        if not weight == None:
            if safe == False:
                uppery = (((ptA[1] + ptB[1])/2)-t.center[1])/3*4+t.center[1]
                lowery = (((ptC[1] + ptD[1])/2)-t.center[1])/3*4+t.center[1]

                upperx = (((ptA[0] + ptD[0])/2)-t.center[0])/3*4+t.center[0]
                lowerx = (((ptB[0] + ptC[0])/2)-t.center[0])/3*4+t.center[0]
            else:
                uppery = (((ptA[1] + ptB[1])/2)-t.center[1])/3*2.5+t.center[1]
                lowery = (((ptC[1] + ptD[1])/2)-t.center[1])/3*2.5+t.center[1]

                upperx = (((ptA[0] + ptD[0])/2)-t.center[0])/3*2.5+t.center[0]
                lowerx = (((ptB[0] + ptC[0])/2)-t.center[0])/3*2.5+t.center[0]

            weights = [weight, 1-weight]
            if mode == 0:
                tpos = [int(t.center[0]), int(np.average([uppery, lowery], weights = weights))]
            if mode == 1:
                tpos = [int(upperx), int(np.average([uppery, lowery], weights = weights))]
            elif mode == 2:
                tpos = [int(lowerx), int(np.average([uppery, lowery], weights = weights))]
            elif mode == 3:
                tpos = [int(np.average([upperx, lowerx], weights = weights)), int(uppery)]
            elif mode == 4:
                tpos = [int(np.average([upperx, lowerx], weights = weights)), int(lowery)]
    if 0 > tpos[0]:
        tpos = [0, tpos[1]]
    if 0 > tpos[1]:
        tpos = [tpos[0], 0]
    if pt.shape[1] <= tpos[0]:
        tpos = [pt.shape[1]-1, tpos[1]]
    if pt.shape[0] <= tpos[1]:
        tpos = [tpos[0], pt.shape[0]-1]
    loop = 0
    while pt[tpos[1]][tpos[0]][0] == 0:
        loop += 1
        if loop > pt.shape[1]:
            break
        if tpos[0] < pt.shape[0] /2:#mode == 1:
            tpos = [tpos[0]+1, tpos[1]]
        else:
            tpos = [tpos[0]-1, tpos[1]]
    dst = pt[tpos[1]][tpos[0]]
    dst = [dst[2], dst[0], -dst[1]]
    dst = np.float64(dst)/1000
    return dst, tpos



def Process(q, o, tq):
    to = Queue()
    twotag = False
    ir_cutoff = 1000
    QueueIn = [0]
    global lastyaw
    lastyaw = 0
    framenum = -90

    f = open('/home/team5927/KVision_v2/2023-chargedup.json')
    Tagjson = json.load(f)

    TagLocations = {}

    for tagitem in Tagjson["tags"]:
        tagtranslation = list(tagitem["pose"]["translation"].values())

        tagrotation_q = list(tagitem["pose"]["rotation"]["quaternion"].values())
        yaw, pitch, roll = PointMath3d.euler_from_quaternion(tagrotation_q[0], tagrotation_q[1], tagrotation_q[2], tagrotation_q[3])
        tagrotation_e = [90-math.degrees(yaw), math.degrees(pitch), math.degrees(roll)]
        TagLocations[tagitem["ID"]] = {"t":tagtranslation, "r":tagrotation_e}
    print(TagLocations)
    while True:
        #framenum += 1
        #if framenum > 180:
        #    framenum = -180
        tq.put([True, "Tag8rot", framenum])
        #Config Stuff

        tq.put([False, "*", to])

        QueueIn = q.get()
        if QueueIn == None:
            break

        Table = to.get()
        usetag8 = Table["Tag8"]
        usetag7 = Table["Tag7"]
        usetag6 = Table["Tag6"]
        usetag5 = Table["Tag5"]
        usetag4 = Table["Tag4"]
        usetag3 = Table["Tag3"]
        usetag2 = Table["Tag2"]
        usetag1 = Table["Tag1"]
        zmin = Table["Z Min"]
        zmax = Table["Z Max"]
        yawpass = int(Table["Multipoint Samples"])
        fastirlightfalloff = Table["Fast Inverse Light Falloff"]

        irimg = QueueIn[0]
        pointimg = QueueIn[1]
        depthimg = QueueIn[2]
        fovmode = QueueIn[3]

        #irimg = (irimg * ((depthimg/ (128*32))**1.5))
        if not fastirlightfalloff:
            if fovmode == "NFOV" or fovmode == "ENFOV":
                depthstep = cv2.multiply(depthimg, (1/(128*32)), dtype=cv2.CV_32F)
            elif fovmode == "WFOV" or fovmode == "EWFOV":
                depthstep = cv2.multiply(depthimg, (1/(128*16)), dtype=cv2.CV_32F)
            depthstep = cv2.pow(depthstep, 2)
            irimg = cv2.multiply(irimg, depthstep, dtype=cv2.CV_8U)
        else:
            #if fovmode == "NFOV" or fovmode == "ENFOV":
            #    depthstep = np.right_shift(depthimg, 6)#cv2.divide(depthimg, 5000, dtype=cv2.CV_8U)
            #elif fovmode == "WFOV" or fovmode == "EWFOV":
            #    depthstep = cv2.divide(depthimg, 2500, dtype=cv2.CV_8U)
            #depthstep = cv2.multiply(depthstep, depthstep)
            #depthstep = cv2.add(depthstep, 1)
            irimg = np.left_shift(cv2.divide(irimg, 4), cv2.divide(depthimg, 4096), dtype=np.uint8)
            #irimg = np.uint8((depthimg/255)**2)

        #depthimg = cv2.pow(depthimg, 2)
        #if fovmode == "NFOV" or fovmode == "ENFOV":
        #    depthstep = cv2.divide(depthimg, 1000/50, dtype=cv2.CV_8U)
        #elif fovmode == "WFOV" or fovmode == "EWFOV":
        #    depthstep = cv2.divide(depthimg, 1000/125, dtype=cv2.CV_8U)
        #depthimg = cv2.add(depthimg, 0.1, dtype=cv2.CV_16U)
        #irimg = irimg / depthimg
        #irimg = cv2.multiply(irimg, depthstep, dtype=cv2.CV_16U)
        #irimg = cv2.divide(irimg, 128, dtype=cv2.CV_8U)

        tdr = tagdetector.detect(irimg) #Tag Detector Results
        ftdr = [] #Filtered Tag Detector Results
        tdst = [] #Tag Distence
        for r in tdr:
            if (((r.tag_id == 8 and usetag8) or (r.tag_id == 7 and usetag7) or (r.tag_id == 6 and usetag6) or (r.tag_id == 5 and usetag5) or (r.tag_id == 4 and usetag4) or (r.tag_id == 3 and usetag3) or (r.tag_id == 2 and usetag2) or (r.tag_id == 1 and usetag1)) and (int(r.hamming) <= 0.25)):

                pt = az_TagToPointCloudPos(r, pointimg)[0]
                dst = math.sqrt(pt[0]**2 + pt[1]**2 + pt[2]**2)
                if True:#zmin < PointMath3d.applyCameraOrientation(pt, 0, -6.5)[2] < zmax:
                    if dst <= 5:
                        irimg = cv2.circle(irimg, [int(r.center[0]), int(r.center[1])], 10, 255, 2)
                        ftdr.append(r)
                        tdst.append(dst)
                    else:
                        irimg = cv2.circle(irimg, [int(r.center[0]), int(r.center[1])], 10, 255/4*3, 2)
                else:
                    irimg = cv2.circle(irimg, [int(r.center[0]), int(r.center[1])], 10, 255/2, 2)
            else:
                irimg = cv2.circle(irimg, [int(r.center[0]), int(r.center[1])], 10, 255/4, 2)
        tdst = np.asarray(tdst)
        tdstin = tdst.argsort()
        if len(ftdr) >= 1:
            pt0, tpos = az_TagToPointCloudPos(ftdr[tdstin[0]], pointimg)
            pts1 = []
            pts2 = []
            rounder = 3
            if len(ftdr) == 1:
                for x in range(0, yawpass):
                    weight = (1/(yawpass-1))*x
                    pt1, tpt1 = az_TagToPointCloudPos(ftdr[tdstin[0]], pointimg, mode = 1, weight = weight)
                    pt2, tpt2 = az_TagToPointCloudPos(ftdr[tdstin[0]], pointimg, mode = 2, weight = weight)
                    #print(math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2 + (pt2[2] - pt1[2])**2))
                    if not math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2 + (pt2[2] - pt1[2])**2) <= 0.235:
                        #continue
                        pt1, tpt1 = az_TagToPointCloudPos(ftdr[tdstin[0]], pointimg, mode = 1, weight = weight, safe = True)
                        pt2, tpt2 = az_TagToPointCloudPos(ftdr[tdstin[0]], pointimg, mode = 2, weight = weight, safe = True)
                    pt3 = pt2-pt1

                    pts1.append(pt3[1])
                    pts2.append(pt3[0])

                    irimg = cv2.line(irimg, np.uint16(tpt1), np.uint16(tpt2), 255, 1)
            else:
                for x in range(0, yawpass):
                    weight = (1/(yawpass-1))*x
                    pt1, tpt1 = az_TagToPointCloudPos(ftdr[1], pointimg, mode = 0, weight = weight)
                    pt2, tpt2 = az_TagToPointCloudPos(ftdr[0], pointimg, mode = 0, weight = weight)
                    pt3 = pt2-pt1

                    pts1.append(pt3[1])
                    pts2.append(pt3[0])

                    irimg = cv2.line(irimg, np.uint16(tpt1), np.uint16(tpt2), 255, 1)
            if pts1:

                yaws = np.degrees(np.arctan2(pts1, pts2))
                #yaws = yaws[abs(yaws - np.mean(yaws)) < 2 * np.std(yaws)]
                yaw = np.average(yaws)
                if not rounder == 0:
                    if yaw > lastyaw:
                        yaw = math.floor(yaw*rounder)/rounder
                    else:
                        yaw = math.ceil(yaw*rounder)/rounder
            else:
                yaw = lastyaw
            lastyaw = yaw

            if ftdr[0].tag_id == 4 or ftdr[0].tag_id == 3 or ftdr[0].tag_id == 2 or ftdr[0].tag_id == 1:
                if len(ftdr) >= 2:
                    yaw = yaw - (math.atan2( FieldGeometry.QRS[int(ftdr[0].tag_id-1)].y/100 - FieldGeometry.QRS[int(ftdr[1].tag_id-1)].y/100,
                           FieldGeometry.QRS[int(ftdr[0].tag_id-1)].x/100 - FieldGeometry.QRS[int(ftdr[1].tag_id-1)].x/100 ) * ( 180 / math.pi ) + 90)
                yaw = -yaw
            else:
                if len(ftdr) >= 2:
                    yaw = yaw - (math.degrees((math.atan2(TagLocations[ftdr[tdstin[0]].tag_id]["t"][1] - TagLocations[ftdr[tdstin[1]].tag_id]["t"][1],
                           TagLocations[ftdr[tdstin[0]].tag_id]["t"][0] - TagLocations[ftdr[tdstin[1]].tag_id]["t"][0] ))))+90
                    print(math.degrees(math.atan2(TagLocations[ftdr[tdstin[0]].tag_id]["t"][1] - TagLocations[ftdr[tdstin[1]].tag_id]["t"][1],
                           TagLocations[ftdr[tdstin[0]].tag_id]["t"][0] - TagLocations[ftdr[tdstin[1]].tag_id]["t"][0] )))
                yaw = -yaw-(TagLocations[ftdr[0].tag_id]["r"][0]-90)

            if yaw < 0:
                globalyaw = -(180+yaw)
            else:
                globalyaw = 90-(yaw-90)
            pt0g = PointMath3d.applyCameraOrientation(pt0, yaw, -6.5)
            #camerarotoffset = PointMath3d.applyCameraOrientation([-0.18+0.05, 0.16+0.065, 0], globalyaw)

            pos = [TagLocations[ftdr[tdstin[0]].tag_id]["t"][0]+(pt0g[1]), TagLocations[ftdr[tdstin[0]].tag_id]["t"][1]+(pt0g[0]), TagLocations[ftdr[tdstin[0]].tag_id]["t"][2]-pt0g[2]]
            #pos = np.subtract(pos, camerarotoffset).tolist()

            tpos = [int(ftdr[tdstin[0]].center[0]), int(ftdr[tdstin[0]].center[1])]

            o.put([irimg, pos, -globalyaw, math.sqrt(pointimg[tpos[1], tpos[0], 0]**2 + pointimg[tpos[1], tpos[0], 2]**2), [pos[0], pos[1], -globalyaw, depthimg[tpos[1], tpos[0]], len(ftdr)]])
        else:
            o.put([np.uint8(irimg)])
