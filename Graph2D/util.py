
import sys
import math
import struct 

def uintBitsToFloat(b):
   s = struct.pack('>I', b)
   return struct.unpack('>f', s)[0]

def cpTorgba(c):
    a = 0 & 0x00000000
    a = a | ( (int(c[0]) & 0xff) << 24)
    a = a | ( (int(c[1]) & 0xff) << 16)
    a = a | ( (int(c[2]) & 0xff) << 8)
    a = a | ( (int(c[3]) & 0xff) )

    return uintBitsToFloat(a)

def cpTorgb(c):
    a = 0x00000000
    a = a | ( c[0] << 16)
    a = a | ( c[1] << 8)
    a = a | ( c[2]  )
    #print(a.to_bytes(4, 'big'))
    return a
def rgbTocp(rgb):
    cp=[]
    cp.append( float(0xff & ( rgb >> 16))/255. )
    cp.append( float(0xff & ( rgb >> 8))/255. )
    cp.append( float(0xff & rgb)/255. )
    cp.append( 1)
    cp.append( 1.)
    return cp

def vDot(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]

def vPerp(v):
    return [v[1], -v[0]]

def vSub(a, b):
    t = [None]*2
    t[0] = a[0] - b[0]
    t[1] = a[1] - b[1]
    return t

def vAdd(a, b):
    t = [None]*2
    t[0] = b[0] + a[0]
    t[1] = b[1] + a[1]
    return t

def vMul(a, b):
    t = [None]*2
    t[0], t[1] = a[0]*b, a[1]*b
    return t

def vUnitforangle(angle):
    return [math.cos(angle), math.sin(angle)]

def square_distance(a, b):
    xd = (a[0] - b[0])*(a[0] - b[0])
    yd = (a[1] - b[1])*(a[1] - b[1])
    zd = (a[2] - b[2])*(a[2] - b[2])
    return xd+yd+zd


def vNomalize(t):
    v = [0]*2
    len = math.sqrt(t[0]*t[0] + t[1]*t[1])
    v[0] = 1.0*t[0]/(len + sys.float_info.min)
    v[1] = 1.0*t[1]/(len + sys.float_info.min)
    return v

def rectangular_to_spherical(v:list) -> list :
    import math
    rho:float = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) 
    phi = math.acos(v[2]/rho)
    if( math.sin(phi) == 0 ) : theta = 0;
    else : theta = math.acos( v[0] / (rho*math.sin(phi)) )
    if(v[1] < 0) :
        theta = 2*math.pi - theta
    return [ rho, theta, phi ]

