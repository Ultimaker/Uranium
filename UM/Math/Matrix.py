# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import math

import numpy

from UM.Math.Vector import Vector

from typing import cast, Dict, List, Optional, Tuple, TYPE_CHECKING, Union

numpy.seterr(divide="ignore")

if TYPE_CHECKING:
    from UM.Math.Quaternion import Quaternion


class Matrix:
    """This class is a 4x4 homogeneous matrix wrapper around numpy.

    Heavily based (in most cases a straight copy with some refactoring) on the excellent
    'library' Transformations.py created by Christoph Gohlke.
    """

    # epsilon for testing whether a number is close to zero
    _EPS = numpy.finfo(float).eps * 4.0

    # map axes strings to/from tuples of inner axis, parity, repetition, frame
    # A triple of Euler angles can be applied/interpreted in 24 ways, which can
    # be specified using a 4 character string or encoded 4-tuple:
    # *Axes 4-string*: e.g. 'sxyz' or 'ryxy'
    # - first character : rotations are applied to 's'tatic or 'r'otating frame
    # - remaining characters : successive rotation axis 'x', 'y', or 'z'
    # *Axes 4-tuple*: e.g. (0, 0, 0, 0) or (1, 1, 1, 1)
    # - inner axis: code of axis ('x':0, 'y':1, 'z':2) of rightmost matrix.
    # - parity : even (0) if inner axis 'x' is followed by 'y', 'y' is followed
    # by 'z', or 'z' is followed by 'x'. Otherwise odd (1).
    # - repetition : first and last axis are same (1) or different (0).
    # - frame : rotations are applied to static (0) or rotating (1) frame.
    _AXES2TUPLE = {
        "sxyz": (0, 0, 0, 0), "sxyx": (0, 0, 1, 0), "sxzy": (0, 1, 0, 0),
        "sxzx": (0, 1, 1, 0), "syzx": (1, 0, 0, 0), "syzy": (1, 0, 1, 0),
        "syxz": (1, 1, 0, 0), "syxy": (1, 1, 1, 0), "szxy": (2, 0, 0, 0),
        "szxz": (2, 0, 1, 0), "szyx": (2, 1, 0, 0), "szyz": (2, 1, 1, 0),
        "rzyx": (0, 0, 0, 1), "rxyx": (0, 0, 1, 1), "ryzx": (0, 1, 0, 1),
        "rxzx": (0, 1, 1, 1), "rxzy": (1, 0, 0, 1), "ryzy": (1, 0, 1, 1),
        "rzxy": (1, 1, 0, 1), "ryxy": (1, 1, 1, 1), "ryxz": (2, 0, 0, 1),
        "rzxz": (2, 0, 1, 1), "rxyz": (2, 1, 0, 1), "rzyz": (2, 1, 1, 1)
    } #type: Dict[str, Tuple[int, int, int, int]]

    # axis sequences for Euler angles
    _NEXT_AXIS = [1, 2, 0, 1]

    def __init__(self, data: Optional[Union[List[List[float]], numpy.array]] = None) -> None:
        if data is None:
            self._data = numpy.identity(4, dtype = numpy.float64)
        else:
            self._data = numpy.array(data, copy=True, dtype = numpy.float64)

    def __deepcopy__(self, memo):
        # So, you must be asking yourself, why not let python handle this simple case on it's own? Well, that's because
        # we found out that this is about 3x faster.
        # Note that actually using Matrix(self._data) (without the deepcopy) is another factor 3 faster.
        return Matrix(self._data)

    def copy(self) -> "Matrix":
        return Matrix(self._data)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if type(other) is not Matrix:
            return False
        other = cast(Matrix, other)

        if self._data is None and other._data is None:
            return True
        return numpy.array_equal(self._data, other._data)

    def at(self, x: int, y: int) -> float:
        if x >= 4 or y >= 4 or x < 0 or y < 0:
            raise IndexError
        return self._data[x,y]

    def setRow(self, index: int, value: List[float]) -> None:
        if index < 0 or index > 3:
            raise IndexError()

        self._data[0, index] = value[0]
        self._data[1, index] = value[1]
        self._data[2, index] = value[2]

        if len(value) > 3:
            self._data[3, index] = value[3]
        else:
            self._data[3, index] = 0

    def setColumn(self, index: int, value: List[float]) -> None:
        if index < 0 or index > 3:
            raise IndexError()

        self._data[index, 0] = value[0]
        self._data[index, 1] = value[1]
        self._data[index, 2] = value[2]

        if len(value) > 3:
            self._data[index, 3] = value[3]
        else:
            self._data[index, 3] = 0

    def multiply(self, other: Union[Vector, "Matrix"], copy: bool = False) -> "Matrix":
        if not copy:
            self._data = numpy.dot(self._data, other.getData())
            return self
        else:
            return Matrix(data = numpy.dot(self._data, other.getData()))

    def preMultiply(self, other: Union[Vector, "Matrix"], copy: bool = False) -> "Matrix":
        if not copy:
            self._data = numpy.dot(other.getData(), self._data)
            return self
        else:
            return Matrix(data = numpy.dot(other.getData(), self._data))

    def getData(self) -> numpy.ndarray:
        """Get raw data.
        :returns: 4x4 numpy array
        """

        return self._data.astype(numpy.float32)

    def setToIdentity(self) -> None:
        """Create a 4x4 identity matrix. This overwrites any existing data."""

        self._data = numpy.identity(4, dtype = numpy.float64)

    def invert(self) -> None:
        """Invert the matrix"""

        self._data = numpy.linalg.inv(self._data)

    def getInverse(self) -> "Matrix":
        """Return a inverted copy of the matrix.
        :returns: The invertex matrix.
        """

        try:
            return Matrix(numpy.linalg.inv(self._data))
        except:
            return Matrix(self._data)

    def getTransposed(self) -> "Matrix":
        """Return the transpose of the matrix."""

        try:
            return Matrix(self._data.transpose())
        except:
            return Matrix(self._data)

    def transpose(self) -> None:
        self._data = self._data.transpose()

    def translate(self, direction: Vector) -> None:
        """Translate the matrix based on Vector.
        :param direction: The vector by which the matrix needs to be translated.
        """

        translation_matrix = Matrix()
        translation_matrix.setByTranslation(direction)
        self.multiply(translation_matrix)

    def setByTranslation(self, direction: Vector) -> None:
        """Set the matrix by translation vector. This overwrites any existing data.
        :param direction: The vector by which the (unit) matrix needs to be translated.
        """

        M = numpy.identity(4, dtype = numpy.float64)
        M[:3, 3] = direction.getData()[:3]
        self._data = M

    def setTranslation(self, translation: Union[Vector, "Matrix"]) -> None:
        self._data[:3, 3] = translation.getData()

    def getTranslation(self) -> Vector:
        return Vector(data = self._data[:3, 3])

    def rotateByAxis(self, angle: float, direction: Vector, point: Optional[List[float]] = None) -> None:
        """Rotate the matrix based on rotation axis
        :param angle: The angle by which matrix needs to be rotated.
        :param direction: Axis by which the matrix needs to be rotated about.
        :param point: Point where from where the rotation happens. If None, origin is used.
        """

        rotation_matrix = Matrix()
        rotation_matrix.setByRotationAxis(angle, direction, point)
        self.multiply(rotation_matrix)

    def setByRotationAxis(self, angle: float, direction: Vector, point: Optional[List[float]] = None) -> None:
        """Set the matrix based on rotation axis. This overwrites any existing data.
        :param angle: The angle by which matrix needs to be rotated in radians.
        :param direction: Axis by which the matrix needs to be rotated about.
        :param point: Point where from where the rotation happens. If None, origin is used.
        """

        sina = math.sin(angle)
        cosa = math.cos(angle)
        direction_data = self._unitVector(direction.getData())
        # rotation matrix around unit vector
        R = numpy.diag([cosa, cosa, cosa])
        R += numpy.outer(direction_data, direction_data) * (1.0 - cosa)
        direction_data *= sina
        R += numpy.array([[ 0.0, -direction_data[2], direction_data[1]],
                        [ direction_data[2], 0.0, -direction_data[0]],
                        [-direction_data[1], direction_data[0], 0.0]], dtype = numpy.float64)
        M = numpy.identity(4)
        M[:3, :3] = R
        if point is not None:
            # rotation not around origin
            point = numpy.array(point[:3], dtype = numpy.float64, copy=False)
            M[:3, 3] = point - numpy.dot(R, point)
        self._data = M

    def compose(self, scale: Vector = None, shear: Vector = None, angles: Vector = None, translate: Vector = None, perspective: Vector = None, mirror: Vector = None) -> None:
        """Return transformation matrix from sequence of transformations.
        This is the inverse of the decompose_matrix function.
        :param scale : vector of 3 scaling factors
        :param shear : list of shear factors for x-y, x-z, y-z axes
        :param angles : list of Euler angles about static x, y, z axes
        :param translate : translation vector along x, y, z axes
        :param perspective : perspective partition of matrix
        :param mirror: vector with mirror factors (1 if that axis is not mirrored, -1 if it is)
        """

        M = numpy.identity(4)
        if perspective is not None:
            P = numpy.identity(4)
            P[3, :] = perspective.getData()[:4]
            M = numpy.dot(M, P)
        if translate is not None:
            T = numpy.identity(4)
            T[:3, 3] = translate.getData()[:3]
            M = numpy.dot(M, T)
        if angles is not None:
            R = Matrix()
            R.setByEuler(angles.x, angles.y, angles.z, "sxyz")
            M = numpy.dot(M, R.getData())
        if shear is not None:
            Z = numpy.identity(4)
            Z[1, 2] = shear.x
            Z[0, 2] = shear.y
            Z[0, 1] = shear.z
            M = numpy.dot(M, Z)
        if scale is not None:
            S = numpy.identity(4)
            S[0, 0] = scale.x
            S[1, 1] = scale.y
            S[2, 2] = scale.z
            M = numpy.dot(M, S)
        if mirror is not None:
            mir = numpy.identity(4)
            mir[0, 0] *= mirror.x
            mir[1, 1] *= mirror.y
            mir[2, 2] *= mirror.z
            M = numpy.dot(M, mir)
        M /= M[3, 3]
        self._data = M

    def getEuler(self, axes: str = "sxyz") -> Vector:
        """Return Euler angles from rotation matrix for specified axis sequence.

        :param axes: One of 24 axis sequences as string or encoded tuple
        Note that many Euler angle triplets can describe one matrix.
        """

        firstaxis, parity, repetition, frame = self._AXES2TUPLE[axes.lower()]

        i = firstaxis
        j = self._NEXT_AXIS[i + parity]
        k = self._NEXT_AXIS[i - parity + 1]

        M = numpy.array(self._data, dtype = numpy.float64, copy = False)[:3, :3]
        if repetition:
            sy = math.sqrt(M[i, j] * M[i, j] + M[i, k] * M[i, k])
            if sy > self._EPS:
                ax = math.atan2( M[i, j],  M[i, k])
                ay = math.atan2( sy,       M[i, i])
                az = math.atan2( M[j, i], -M[k, i])
            else:
                ax = math.atan2(-M[j, k],  M[j, j])
                ay = math.atan2( sy,       M[i, i])
                az = 0.0
        else:
            cy = math.sqrt(M[i, i] * M[i, i] + M[j, i] * M[j, i])
            if cy > self._EPS:
                ax = math.atan2( M[k, j],  M[k, k])
                ay = math.atan2(-M[k, i],  cy)
                az = math.atan2( M[j, i],  M[i, i])
            else:
                ax = math.atan2(-M[j, k],  M[j, j])
                ay = math.atan2(-M[k, i],  cy)
                az = 0.0

        if parity:
            ax, ay, az = -ax, -ay, -az
        if frame:
            ax, az = az, ax
        return Vector(ax, ay, az)

    def setByEuler(self, ai: float, aj: float, ak: float, axes: str = "sxyz") -> None:
        """Return homogeneous rotation matrix from Euler angles and axis sequence.
        :param ai: Eulers roll
        :param aj: Eulers pitch
        :param ak: Eulers yaw
        :param axes: One of 24 axis sequences as string or encoded tuple
        """

        firstaxis, parity, repetition, frame = self._AXES2TUPLE[axes.lower()]
        i = firstaxis
        j = self._NEXT_AXIS[i + parity]
        k = self._NEXT_AXIS[i - parity + 1]

        if frame:
            ai, ak = ak, ai
        if parity:
            ai, aj, ak = -ai, -aj, -ak

        si, sj, sk = math.sin(ai), math.sin(aj), math.sin(ak)
        ci, cj, ck = math.cos(ai), math.cos(aj), math.cos(ak)
        cc, cs = ci * ck, ci * sk
        sc, ss = si * ck, si * sk

        M = numpy.identity(4)
        if repetition:
            M[i, i] = cj
            M[i, j] = sj * si
            M[i, k] = sj * ci
            M[j, i] = sj * sk
            M[j, j] = -cj * ss + cc
            M[j, k] = -cj * cs - sc
            M[k, i] = -sj * ck
            M[k, j] = cj * sc + cs
            M[k, k] = cj * cc - ss
        else:
            M[i, i] = cj * ck
            M[i, j] = sj * sc - cs
            M[i, k] = sj * cc + ss
            M[j, i] = cj * sk
            M[j, j] = sj * ss + cc
            M[j, k] = sj * cs - sc
            M[k, i] = -sj
            M[k, j] = cj * si
            M[k, k] = cj * ci
        self._data = M

    def scaleByFactor(self, factor: float, origin: Optional[List[float]] = None, direction: Optional[Vector] = None) -> None:
        """Scale the matrix by factor wrt origin & direction.

        :param factor: The factor by which to scale
        :param origin: From where does the scaling need to be done
        :param direction: In what direction is the scaling (if None, it's uniform)
        """

        scale_matrix = Matrix()
        scale_matrix.setByScaleFactor(factor, origin, direction)
        self.multiply(scale_matrix)

    def setByScaleFactor(self, factor: float, origin: Optional[List[float]] = None, direction: Optional[Vector] = None) -> None:
        """Set the matrix by scale by factor wrt origin & direction. This overwrites any existing data

        :param factor: The factor by which to scale
        :param origin: From where does the scaling need to be done
        :param direction: In what direction is the scaling (if None, it's uniform)
        """

        if direction is None:
            # uniform scaling
            M = numpy.diag([factor, factor, factor, 1.0])
            if origin is not None:
                M[:3, 3] = origin[:3]
                M[:3, 3] *= 1.0 - factor
        else:
            # nonuniform scaling
            direction_data = direction.getData()
            factor = 1.0 - factor
            M = numpy.identity(4, dtype = numpy.float64)
            M[:3, :3] -= factor * numpy.outer(direction_data, direction_data)
            if origin is not None:
                M[:3, 3] = (factor * numpy.dot(origin[:3], direction_data)) * direction_data
        self._data = M

    def setByScaleVector(self, scale: Vector) -> None:
        self._data = numpy.diag([scale.x, scale.y, scale.z, 1.0])

    def getScale(self) -> Vector:
        x = numpy.linalg.norm(self._data[0,0:3])
        y = numpy.linalg.norm(self._data[1,0:3])
        z = numpy.linalg.norm(self._data[2,0:3])

        return Vector(x, y, z)

    def setOrtho(self, left: float, right: float, bottom: float, top: float, near: float, far: float) -> None:
        """Set the matrix to an orthographic projection. This overwrites any existing data.

        :param left: The left edge of the projection
        :param right: The right edge of the projection
        :param top: The top edge of the projection
        :param bottom: The bottom edge of the projection
        :param near: The near plane of the projection
        :param far: The far plane of the projection
        """

        self.setToIdentity()
        self._data[0, 0] = 2 / (right - left)
        self._data[1, 1] = 2 / (top - bottom)
        self._data[2, 2] = -2 / (far - near)
        self._data[3, 0] = -((right + left) / (right - left))
        self._data[3, 1] = -((top + bottom) / (top - bottom))
        self._data[3, 2] = -((far + near) / (far - near))

    def setPerspective(self, fovy: float, aspect: float, near: float, far: float) -> None:
        """Set the matrix to a perspective projection. This overwrites any existing data.

        :param fovy: Field of view in the Y direction
        :param aspect: The aspect ratio
        :param near: Distance to the near plane
        :param far: Distance to the far plane
        """

        self.setToIdentity()

        f = 2. / math.tan(math.radians(fovy) / 2.)

        self._data[0, 0] = f / aspect
        self._data[1, 1] = f
        self._data[2, 2] = (far + near) / (near - far)
        self._data[2, 3] = -1.
        self._data[3, 2] = (2. * far * near) / (near - far)

    def decompose(self) -> Tuple[Vector, "Matrix", Vector, Vector]:
        """
        SOURCE: https://github.com/matthew-brett/transforms3d/blob/e402e56686648d9a88aa048068333b41daa69d1a/transforms3d/affines.py
        Decompose 4x4 homogenous affine matrix into parts.
        The parts are translations, rotations, zooms, shears.
        This is the same as :func:`decompose` but specialized for 4x4 affines.
        Decomposes `A44` into ``T, R, Z, S``, such that::
           Smat = np.array([[1, S[0], S[1]],
                            [0,    1, S[2]],
                            [0,    0,    1]])
           RZS = np.dot(R, np.dot(np.diag(Z), Smat))
           A44 = np.eye(4)
           A44[:3,:3] = RZS
           A44[:-1,-1] = T
        The order of transformations is therefore shears, followed by
        zooms, followed by rotations, followed by translations.
        This routine only works for shape (4,4) matrices
        Parameters
        ----------
        A44 : array shape (4,4)
        Returns
        -------
        T : array, shape (3,)
           Translation vector
        R : array shape (3,3)
            rotation matrix
        Z : array, shape (3,)
           Zoom vector.  May have one negative zoom to prevent need for negative
           determinant R matrix above
        S : array, shape (3,)
           Shear vector, such that shears fill upper triangle above
           diagonal to form shear matrix (type ``striu``).
        """
        A44 = numpy.asarray(self._data, dtype = numpy.float64)
        T = A44[:-1, -1]
        RZS = A44[:-1, :-1]
        # compute scales and shears
        M0, M1, M2 = numpy.array(RZS).T
        # extract x scale and normalize
        sx = math.sqrt(numpy.sum(M0 ** 2))
        M0 /= sx
        # orthogonalize M1 with respect to M0
        sx_sxy = numpy.dot(M0, M1)
        M1 -= sx_sxy * M0
        # extract y scale and normalize
        sy = math.sqrt(numpy.sum(M1 ** 2))
        M1 /= sy
        sxy = sx_sxy / sx
        # orthogonalize M2 with respect to M0 and M1
        sx_sxz = numpy.dot(M0, M2)
        sy_syz = numpy.dot(M1, M2)
        M2 -= (sx_sxz * M0 + sy_syz * M1)
        # extract z scale and normalize
        sz = math.sqrt(numpy.sum(M2 ** 2))
        M2 /= sz
        sxz = sx_sxz / sx
        syz = sy_syz / sy
        # Reconstruct rotation matrix, ensure positive determinant
        Rmat = numpy.array([M0, M1, M2]).T

        # The original code ensures that the determinant is positive, but I can't find a single situation where this
        # is actualy used / needed by us. It is, however, one of the more expensive parts of this function.
        #if numpy.linalg.det(Rmat) < 0:
        #    sx *= -1
        #    Rmat[:, 0] *= -1

        return Vector(data = T), Matrix(data=Rmat), Vector(data = numpy.array([sx, sy, sz])), Vector(data=numpy.array([sxy, sxz, syz]))

    def _unitVector(self, data: numpy.array, axis: Optional[int] = None, out: Optional[numpy.array] = None) -> numpy.array:
        """Return ndarray normalized by length, i.e. Euclidean norm, along axis.
        >>> matrix = Matrix()
        >>> v0 = numpy.random.random(3)
        >>> v1 = matrix._unitVector(v0)
        >>> numpy.allclose(v1, v0 / numpy.linalg.norm(v0))
        True
        >>> v0 = numpy.random.rand(5, 4, 3)
        >>> v1 = matrix._unitVector(v0, axis=-1)
        >>> v2 = v0 / numpy.expand_dims(numpy.sqrt(numpy.sum(v0 * v0, axis=2)), 2)
        >>> numpy.allclose(v1, v2)
        True
        >>> v1 = matrix._unitVector(v0, axis=1)
        >>> v2 = v0 / numpy.expand_dims(numpy.sqrt(numpy.sum(v0 * v0, axis=1)), 1)
        >>> numpy.allclose(v1, v2)
        True
        >>> v1 = numpy.empty((5, 4, 3))
        >>> matrix._unitVector(v0, axis=1, out=v1)
        >>> numpy.allclose(v1, v2)
        True
        >>> list(matrix._unitVector([]))
        []
        >>> list(matrix._unitVector([1]))
        [1.0]
        """
        if out is None:
            data = numpy.array(data, dtype = numpy.float64, copy = True)
            if data.ndim == 1:
                data /= math.sqrt(numpy.dot(data, data))
                return data
        else:
            if out is not data:
                out[:] = numpy.array(data, copy = False)
            data = out
        length = numpy.atleast_1d(numpy.sum(data*data, axis))
        numpy.sqrt(length, length)
        if axis is not None:
            length = numpy.expand_dims(length, axis)
        data /= length
        if out is None:
            return data

    def __repr__(self) -> str:
        return "Matrix( {0} )".format(self._data)

    @staticmethod
    def fromPositionOrientationScale(position: Vector, orientation: "Quaternion", scale: Vector) -> "Matrix":
        s = numpy.identity(4, dtype = numpy.float64)
        s[0, 0] = scale.x
        s[1, 1] = scale.y
        s[2, 2] = scale.z

        r = orientation.toMatrix().getData()

        t = numpy.identity(4, dtype = numpy.float64)
        t[0, 3] = position.x
        t[1, 3] = position.y
        t[2, 3] = position.z

        return Matrix(data = numpy.dot(numpy.dot(t, r), s))
