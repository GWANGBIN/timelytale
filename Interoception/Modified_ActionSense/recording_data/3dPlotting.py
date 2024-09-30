import math as m
import numpy as np

def _rotation_X(theta):
    theta = -theta
    return np.matrix([[1, 0, 0],
                      [0, m.cos(m.pi * (theta / 180)), -m.sin(m.pi * (theta / 180))],
                      [0, m.sin(m.pi * (theta / 180)), m.cos(m.pi * (theta / 180))]])


def _rotation_Y(theta):
    theta = -theta
    return np.matrix([[m.cos(m.pi * (theta / 180)), 0, m.sin(m.pi * (theta / 180))],
                      [0, 1, 0],
                      [-m.sin(m.pi * (theta / 180)), 0, m.cos(m.pi * (theta / 180))]])


def _rotation_Z(theta):
    theta = -theta
    return np.matrix([[m.cos(m.pi * (theta / 180)), -m.sin(m.pi * (theta / 180)), 0],
                      [m.sin(m.pi * (theta / 180)), m.cos(m.pi * (theta / 180)), 0],
                      [0, 0, 1]])

def _rotationMatrix(euler):
        return _rotation_Z(euler[2]) @ _rotation_Y(euler[1]) @ _rotation_X(euler[0])


def quaternion_rotation_matrix(Q):
    """
    Covert a quaternion into a full three-dimensional rotation matrix.

    Input
    :param Q: A 4 element array representing the quaternion (q0,q1,q2,q3)

    Output
    :return: A 3x3 element matrix representing the full 3D rotation matrix.
             This rotation matrix converts a point in the local reference
             frame to a point in the global reference frame.
    """
    # Extract the values from Q
    q0 = Q[0]
    q1 = Q[1]
    q2 = Q[2]
    q3 = Q[3]

    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)

    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)

    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1

    # 3x3 rotation matrix
    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])

    return rot_matrix

localPosParent = np.array([-7.405253,	96.97312, -0.67008424])
localPosChild = np.array([-10.9992485,	0.011121482, 0.0030256808])
localEuler = [133.06927, -94.16079,	133.81085]
localQuternion = [-0.51155156,	0.46021417,	0.51325375,	0.5129215]

localPosParent1 = np.array([-10.9992485,	0.011121482, 0.0030256808])
localPosChild1 = np.array([7.9348683E-4,	-45.061256,	4.5895576E-4])
localEuler1 = [92.59265,	179.62453,	88.184395]
localQuternion1 = [0.50464386,	0.49788514,	-0.47905472, -0.51764035]

localPosParent2 = np.array([7.9348683E-4,	-45.061256,	4.5895576E-4])
localPosChild2 = np.array([0.0016141217, -42.058643, -0.0010374933])
localEuler2 = [149.27043, 92.750725, -58.957447]
localQuternion2 = [-0.18434736,	-0.16041072,	0.6735297,	-0.69759744]

GlobalPos = _rotationMatrix(localEuler) @ (localPosChild)
GlobalPos1 = _rotationMatrix(localEuler) @ _rotationMatrix(localEuler1) @ (localPosChild1)
GlobalPos2 = _rotationMatrix(localEuler) @ _rotationMatrix(localEuler1) @ _rotationMatrix(localEuler2) @ (localPosChild2)

GlobalPos_ = quaternion_rotation_matrix(localQuternion) @ localPosChild
GlobalPos1_= quaternion_rotation_matrix(localQuternion1) @ localPosChild
GlobalPos2_= quaternion_rotation_matrix(localQuternion2) @ localPosChild

JointPos  = [-0.0737859*100,   0.969748*100,	-0.00658686*100]
JointPos1 = [-0.0791746*100,   0.968597*100,	-0.116441*100]
JointPos2 = [-0.0862783*100,   0.966261*100,	-0.566993*100]
JointPos3 = [-0.10668*100,	   0.546197*100,	-0.561909*100]

print(localPosParent)
print(list(np.ravel(GlobalPos_)))
# print(list(np.ravel(localPosParent+GlobalPos_)))
print(list(np.ravel(GlobalPos1_)))
# print(list(np.ravel(localPosParent+GlobalPos_+GlobalPos1_)))
print(list(np.ravel(GlobalPos2_)))
# print(list(np.ravel(localPosParent+GlobalPos_+GlobalPos1_+GlobalPos2_)))