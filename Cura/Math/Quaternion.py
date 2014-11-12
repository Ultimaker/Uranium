# Wrapper for Quaternion
class Quaternion(object):
    def __init__(self):
        self._data = numpy.zeros((4, ))
    
    # Set quaternion by providing rotation about an axis.
    # \example q.setByAxis(0.123,[1,0,0])
    def setByAxis(self,angle, axis):
        q = numpy.array([0.0, axis[0], axis[1], axis[2]])
        qlen = vector_norm(q)
        if qlen > _EPS:
            q *= math.sin(angle/2.0) / qlen
        q[0] = math.cos(angle/2.0)
        self._data = q
    
    def multiply(self, quaternion):
        w0, x0, y0, z0 = quaternion
        w1, x1, y1, z1 = self._data
        self._data = numpy.array([-x1*x0 - y1*y0 - z1*z0 + w1*w0,
                         x1*w0 + y1*z0 - z1*y0 + w1*x0,
                        -x1*z0 + y1*w0 + z1*x0 + w1*y0,
                         x1*y0 - y1*x0 + z1*w0 + w1*z0], dtype=numpy.float64)
    
    # Set quaternion by providing a homogenous (4x4) rotation matrix.
    def setByMatrix(self,matrix, isprecise=False):
        M = numpy.array(matrix.getData(), dtype=numpy.float64, copy=False)[:4, :4]
        if isprecise:
            q = numpy.empty((4, ))
            t = numpy.trace(M)
            if t > M[3, 3]:
                q[0] = t
                q[3] = M[1, 0] - M[0, 1]
                q[2] = M[0, 2] - M[2, 0]
                q[1] = M[2, 1] - M[1, 2]
            else:
                i, j, k = 1, 2, 3
                if M[1, 1] > M[0, 0]:
                    i, j, k = 2, 3, 1
                if M[2, 2] > M[i, i]:
                    i, j, k = 3, 1, 2
                t = M[i, i] - (M[j, j] + M[k, k]) + M[3, 3]
                q[i] = t
                q[j] = M[i, j] + M[j, i]
                q[k] = M[k, i] + M[i, k]
                q[3] = M[k, j] - M[j, k]
            q *= 0.5 / math.sqrt(t * M[3, 3])
        else:
            m00 = M[0, 0]
            m01 = M[0, 1]
            m02 = M[0, 2]
            m10 = M[1, 0]
            m11 = M[1, 1]
            m12 = M[1, 2]
            m20 = M[2, 0]
            m21 = M[2, 1]
            m22 = M[2, 2]
            # symmetric matrix K
            K = numpy.array([[m00-m11-m22, 0.0,         0.0,         0.0],
                            [m01+m10,     m11-m00-m22, 0.0,         0.0],
                            [m02+m20,     m12+m21,     m22-m00-m11, 0.0],
                            [m21-m12,     m02-m20,     m10-m01,     m00+m11+m22]])
            K /= 3.0
            # quaternion is eigenvector of K that corresponds to largest eigenvalue
            w, V = numpy.linalg.eigh(K)
            q = V[[3, 0, 1, 2], numpy.argmax(w)]
        if q[0] < 0.0:
            numpy.negative(q, q)
        self._data = q