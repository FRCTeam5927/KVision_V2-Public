import numpy as np
import math
CameraPosition = {
        "x": 0, # actual position in meters of kinect sensor relative to the viewport's center.
        "y": 0, # actual position in meters of kinect sensor relative to the viewport's center.
        "z": 0, # height in meters of actual kinect sensor from the floor.
        "roll": 0, # angle in degrees of sensor's roll (used for INU input - trig function for this is commented out by default).
        "azimuth": 0, # sensor's yaw angle in degrees.
        "elevation": 0, # sensor's pitch angle in degrees.
    }
def depthToPointCloudPos(x_d, y_d, z, CameraParams, scale=1000):
    x = (x_d - CameraParams['cx']) * z / CameraParams['fx']
    y = (y_d - CameraParams['cy']) * z / CameraParams['fy']

    return [x / scale, y / scale, z / scale]

def applyCameraOrientation(pt, yaw, pitch = 0):
    pt_orig = pt
    # Kinect Sensor Orientation Compensation
    # This runs slowly in Python as it is required to be called within a loop, but it is a more intuitive example than it's vertorized alternative (Purly for example)
    # use trig to rotate a vertex around a gimbal.
    def rotatePoints(ax1, ax2, deg):
        # math to rotate vertexes around a center point on a plane.
        hyp = np.sqrt(pt[ax1] ** 2 + pt[ax2] ** 2) # Get the length of the hypotenuse of the real-world coordinate from center of rotation, this is the radius!
        d_tan = np.arctan2(pt[ax2], pt[ax1]) # Calculate the vertexes current angle (returns radians that go from -180 to 180)

        cur_angle = np.degrees(d_tan) % 360 # Convert radians to degrees and use modulo to adjust range from 0 to 360.
        new_angle = np.radians((cur_angle + deg) % 360) # The new angle (in radians) of the vertexes after being rotated by the value of deg.

        pt[ax1] = hyp * np.cos(new_angle) # Calculate the rotated coordinate for this axis.
        pt[ax2] = hyp * np.sin(new_angle) # Calculate the rotated coordinate for this axis.
    #rotatePoints(1, 2, CameraPosition['roll']) #rotate on the Y&Z plane # Disabled because most tripods don't roll. If an Inertial Nav Unit is available this could be used)
    rotatePoints(0, 2, pitch) #rotate on the X&Z plane
    rotatePoints(0, 1, yaw) #rotate on the X&Y plane

    # Apply offsets for height and linear position of the sensor (from viewport's center)
    pt[:] += np.float_([CameraPosition['x'], CameraPosition['y'], CameraPosition['z']])

    return pt
import cv2
def depthMatrixToPointCloudPos(z, CameraParams, indices, scale=1000):
    # bacically this is a vectorized version of depthToPointCloudPos()
    # calculate the real-world xyz vertex coordinates from the raw depth data matrix.
    z = cv2.divide(z, scale)
    C, R = indices

    #R = np.float32(R)
    #R = cv2.UMat(R)
    R = cv2.subtract(R, CameraParams['cx'])
    R = cv2.multiply(R, z)#, dtype=cv2.CV_32F)
    R = cv2.divide(R, CameraParams['fx'])

    #C = np.float32(C)
    #C = cv2.UMat(C)
    C = cv2.subtract(C, CameraParams['cy'])
    C = cv2.multiply(C, z)#, dtype=cv2.CV_32F)
    C = cv2.divide(C, CameraParams['fy'])
    C = cv2.multiply(C, -1)

    #z = cv2.UMat()
    #z = cv2.divide(z, scale, dtype=cv2.CV_32F)
    #z = np.float64(z)

    return cv2.merge((R, z, C))
    #np.column_stack((z.ravel() / scale, R.ravel(), -C.ravel()))
def rotatePoints2(pt, deg, mode=0):
    x, y, z = cv2.split(pt)
    deg = math.radians(deg)

    cos = math.cos(deg)
    sin = math.sin(deg)

    if mode == 0:
        newx = cv2.subtract(cv2.multiply(x, cos), cv2.multiply(y, sin))
        newy = cv2.add(cv2.multiply(x, sin), cv2.multiply(y, cos))
        return cv2.merge((newx, newy, z))
    elif mode == 1:
        newy = cv2.subtract(cv2.multiply(y, cos), cv2.multiply(z, sin))
        newz = cv2.add(cv2.multiply(y, sin), cv2.multiply(z, cos))
        return cv2.merge((x, newy, newz))
    elif mode == 2:
        newx = cv2.subtract(cv2.multiply(x, cos), cv2.multiply(z, sin))
        newz = cv2.add(cv2.multiply(x, sin), cv2.multiply(z, cos))
        return cv2.merge((newx, y, newz))

#https://stackoverflow.com/questions/34050929/3d-point-rotation-algorithm
def rotatePoints3(pt, rot, Queues):
    cosa = math.cos(rot[0])
    sina = math.sin(rot[0])

    cosb = math.cos(rot[1])
    sinb = math.sin(rot[1])

    cosc = math.cos(rot[2])
    sinc = math.sin(rot[2])

    Axx = cosa*cosb
    Axy = cosa*sinb*sinc - sina*cosc
    Axz = cosa*sinb*cosc + sina*sinc

    Ayx = sina*cosb
    Ayy = sina*sinb*sinc + cosa*cosc
    Ayz = sina*sinb*cosc - cosa*sinc

    Azx = -sinb
    Azy = cosb*sinc
    Azz = cosb*cosc
    x, y, z = cv2.split(pt)
    sept = [x, y, z]
    Queues[0].put([1, Queues[1], sept, [Axx, Axy, Axz]])
    Queues[0].put([1, Queues[2], sept, [Ayx, Ayy, Ayz]])
    Queues[0].put([1, Queues[3], sept, [Azx, Azy, Azz]])
    newx = Queues[1].get()#cv2.add(cv2.add(cv2.multiply(x, Axx), cv2.multiply(y, Axy)), cv2.multiply(z, Axz))
    newy = Queues[2].get()#cv2.add(cv2.add(cv2.multiply(x, Ayx), cv2.multiply(y, Ayy)), cv2.multiply(z, Ayz))
    newz = Queues[3].get()#cv2.add(cv2.add(cv2.multiply(x, Azx), cv2.multiply(y, Azy)), cv2.multiply(z, Azz))
    return cv2.merge((newx, newy, newz))
def applyCameraMatrixOrientation(pt, Yaw, Pitch = 0):
    # Kinect Sensor Orientation Compensation
    # bacically this is a vectorized version of applyCameraOrientation()
    # uses same trig to rotate a vertex around a gimbal.
    def rotatePoints(ax1, ax2, deg):
        # math to rotate vertexes around a center point on a plane.
        hyp = np.sqrt(pt[:, :, ax1] ** 2 + pt[:, :, ax2] ** 2) # Get the length of the hypotenuse of the real-world coordinate from center of rotation, this is the radius!
        d_tan = np.arctan2(pt[:, :, ax2], pt[:, :, ax1]) # Calculate the vertexes current angle (returns radians that go from -180 to 180)

        cur_angle = np.degrees(d_tan) % 360 # Convert radians to degrees and use modulo to adjust range from 0 to 360.
        new_angle = np.radians((cur_angle + deg) % 360) # The new angle (in radians) of the vertexes after being rotated by the value of deg.

        pt[:, :, ax1] = hyp * np.cos(new_angle) # Calculate the rotated coordinate for this axis.
        pt[:, :, ax2] = hyp * np.sin(new_angle) # Calculate the rotated coordinate for this axis.

    #rotatePoints(1, 2, -sdnt.getNumber("Pigeon_Roll", 0)) #rotate on the Y&Z plane # Disabled because most tripods don't roll. If an Inertial Nav Unit is available this could be used)
    #rotatePoints(0, 2, CameraPosition['elevation']) #rotate on the X&Z plane
    #rotatePoints(0, 1, Yaw)# CameraPosition['azimuth']) #rotate on the X&Y
    #1/0
    pt = rotatePoints2(pt, Pitch, 1)
    #pt = rotatePoints2(pt, Yaw)
    # Apply offsets for height and linear position of the sensor (from viewport's center)
    #pt[:] += np.float_([CameraPosition['x'], CameraPosition['y'], CameraPosition['z']])



    return pt

#https://stackoverflow.com/questions/12729228/simple-efficient-bilinear-interpolation-of-images-in-numpy-and-python
def bilinear_interpolate(im, x, y):
    x = np.asarray(x)
    y = np.asarray(y)

    x0 = np.floor(x).astype(int)
    x1 = x0 + 1
    y0 = np.floor(y).astype(int)
    y1 = y0 + 1

    x0 = np.clip(x0, 0, im.shape[1]-1);
    x1 = np.clip(x1, 0, im.shape[1]-1);
    y0 = np.clip(y0, 0, im.shape[0]-1);
    y1 = np.clip(y1, 0, im.shape[0]-1);

    Ia = im[ y0, x0 ]
    Ib = im[ y1, x0 ]
    Ic = im[ y0, x1 ]
    Id = im[ y1, x1 ]

    wa = (x1-x) * (y1-y)
    wb = (x1-x) * (y-y0)
    wc = (x-x0) * (y1-y)
    wd = (x-x0) * (y-y0)

    return wa*Ia + wb*Ib + wc*Ic + wd*Id

#https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/
def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)

        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)

        return roll_x, pitch_y, yaw_z # in radians
