from __future__ import print_function
from __future__ import division
import numpy as np
from sympy import symbols, sin, cos, pi, simplify, trigsimp


class mDH(object):
    """
    This uses the modified DH parameters
    see Craig, eqn (3.6)
    """
    def __init__(self):
        pass

    def fk(self, params):
        t = np.eye(4)
        for p in params:
            t = t.dot(self.makeT(*p))
        return t

    def makeT(self, a, alpha, d, theta):
        return np.array([  # classic DH
            [           cos(theta),           -sin(theta),           0,             a],
            [sin(theta)*cos(alpha), cos(theta)*cos(alpha), -sin(alpha), -d*sin(alpha)],
            [sin(theta)*sin(alpha), cos(theta)*sin(alpha),  cos(alpha),  d*cos(alpha)],
            [                    0,                     0,           0,             1]
        ])

def eval(f):
    """
    This allows you to simplify the trigonomic mess that kinematics can
    create and also substitute in some inputs in the process
    """
    c = []
    for row in f:
        r = []
        for col in row:
            # use python symbolic toolbox to simplify the trig mess above 
            r.append(simplify(col))
        c.append(r)
    return np.array(c)

def subs(f, m):
    """
    This allows you to simplify the trigonomic mess that kinematics can
    create and also substitute in some inputs in the process
    """
    c = []
    for row in f:
        r = []
        for col in row:
            r.append(col.subs(m))
        c.append(r)
    return np.array(c)
    
def printT(tt):
    R = tt[0:3,0:3]
    D = tt[0:3, 3]
    print('-'*30)
    print('Position:')
    print('  x:', D[0])
    print('  y:', D[1])
    print('  z:', D[2])
    # R(n, o, a)
    print('-'*30)
    print('Orientation')
    print('  nx:', R[0,0])
    print('  ny:', R[0,1])
    print('  nz:', R[0,2])
    print('')
    print('  ox:', R[1,0])
    print('  oy:', R[1,1])
    print('  oz:', R[1,2])
    print('')
    print('  ax:', R[2,0])
    print('  ay:', R[2,1])
    print('  az:', R[2,2])