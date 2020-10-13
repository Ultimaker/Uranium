# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Math.Vector import Vector
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Logger import Logger
from UM.Math import NumPyUtil
from UM.Math.Matrix import Matrix

from enum import Enum
from typing import List, Optional, Tuple, Dict, Any

import threading
import numpy
import numpy.linalg
import scipy.spatial
import scipy.spatial.qhull
import hashlib
from time import time
numpy.seterr(all="ignore") # Ignore warnings (dev by zero)

MAXIMUM_HULL_VERTICES_COUNT = 1024   # Maximum number of vertices to have in the convex hull.


class MeshType(Enum):
    faces = 1 # Start at one, as 0 is false (so if this is used in a if statement, it's always true)
    pointcloud = 2


Reuse = object()
"""This object is being used as a 'symbol' to identify parameters have not been explicitly supplied
# to the set() method. We can't use the value None for this purpose because it is also a valid (new)
# value to set a field to in set().
"""


class MeshData:
    """Class to hold a list of verts and possibly how (and if) they are connected.

    This class stores three numpy arrays that contain the data for a mesh. Vertices
    are stored as a two-dimensional array of floats with the rows being individual
    vertices and the three columns being the X, Y and Z components of the vertices.
    Normals are stored in the same manner and kept in sync with the vertices. Indices
    are stored as a two-dimensional array of integers with the rows being the individual
    faces and the three columns being the indices that refer to the individual vertices.

    attributes: a dict with {"value", "opengl_type", "opengl_name"} type in vector2f, vector3f, uniforms, ...
    """

    def __init__(self, vertices=None, normals=None, indices=None, colors=None, uvs=None, file_name=None,
                 center_position=None, zero_position=None, type = MeshType.faces, attributes=None) -> None:
        self._application = None  # Initialize this later otherwise unit tests break

        self._vertices = NumPyUtil.immutableNDArray(vertices)
        self._normals = NumPyUtil.immutableNDArray(normals)
        self._indices = NumPyUtil.immutableNDArray(indices)
        self._colors = NumPyUtil.immutableNDArray(colors)
        self._uvs = NumPyUtil.immutableNDArray(uvs)
        self._vertex_count = len(self._vertices) if self._vertices is not None else 0
        self._face_count = len(self._indices) if self._indices is not None else 0
        self._type = type
        self._file_name = file_name  # type: Optional[str]
        # original center position
        self._center_position = center_position
        # original zero position, is changed after transformation
        if zero_position is not None:
            self._zero_position = zero_position
        else:
            self._zero_position = Vector(0, 0, 0)
        self._convex_hull = None    # type: Optional[scipy.spatial.ConvexHull]
        self._convex_hull_vertices = None  # type: Optional[numpy.ndarray]
        self._convex_hull_lock = threading.Lock()

        self._attributes = {}  # type: Dict[str, Any]
        if attributes is not None:
            for key, attribute in attributes.items():
                new_value = {}
                for attribute_key, attribute_value in attribute.items():
                    if attribute_key == "value":
                        new_value["value"] = NumPyUtil.immutableNDArray(attribute_value)
                    else:
                        new_value[attribute_key] = attribute_value
                self._attributes[key] = new_value

    def __del__(self):
        """Triggered when this file is deleted.

        The file will then no longer be watched for changes.
        """

        if self._file_name:
            if self._application:
                self._application.getController().getScene().removeWatchedFile(self._file_name)

    def set(self, vertices=Reuse, normals=Reuse, indices=Reuse, colors=Reuse, uvs=Reuse, file_name=Reuse,
            center_position=Reuse, zero_position=Reuse, attributes=Reuse) -> "MeshData":
        """Create a new MeshData with specified changes

        :return: :type{MeshData}
        """

        vertices = vertices if vertices is not Reuse else self._vertices
        normals = normals if normals is not Reuse else self._normals
        indices = indices if indices is not Reuse else self._indices
        colors = colors if colors is not Reuse else self._colors
        uvs = uvs if uvs is not Reuse else self._uvs
        file_name = file_name if file_name is not Reuse else self._file_name
        center_position = center_position if center_position is not Reuse else self._center_position
        zero_position = zero_position if zero_position is not Reuse else self._zero_position
        attributes = attributes if attributes is not Reuse else self._attributes

        return MeshData(vertices=vertices, normals=normals, indices=indices, colors=colors, uvs=uvs,
                        file_name=file_name, center_position=center_position, zero_position=zero_position, attributes=attributes)

    def getHash(self):
        m = hashlib.sha256()
        m.update(self.getVerticesAsByteArray())
        return m.hexdigest()

    def getCenterPosition(self) -> Vector:
        return self._center_position

    def getZeroPosition(self) -> Vector:
        return self._zero_position

    def getType(self):
        return self._type

    def getFaceCount(self) -> int:
        return self._face_count

    def getVertices(self) -> numpy.ndarray:
        """Get the array of vertices"""

        return self._vertices

    def getVertexCount(self) -> int:
        """Get the number of vertices"""

        return self._vertex_count

    def getVertex(self, index):
        """Get a vertex by index"""

        try:
            return self._vertices[index]
        except IndexError:
            return None

    def hasNormals(self) -> bool:
        """Return whether this mesh has vertex normals."""

        return self._normals is not None

    def getNormals(self) -> numpy.ndarray:
        """Return the list of vertex normals."""

        return self._normals

    def hasIndices(self) -> bool:
        """Return whether this mesh has indices."""

        return self._indices is not None

    def getIndices(self) -> numpy.ndarray:
        """Get the array of indices

        :return: :type{numpy.ndarray}
        """

        if self._indices is not None and self._indices.dtype != "int32":
            self._indices = numpy.asarray(self._indices, dtype=numpy.int32)
        return self._indices

    def hasColors(self) -> bool:
        return self._colors is not None

    def getColors(self) -> numpy.ndarray:
        return self._colors

    def hasUVCoordinates(self) -> bool:
        return self._uvs is not None

    def getFileName(self) -> Optional[str]:
        return self._file_name

    def getTransformed(self, transformation: Matrix) -> "MeshData":
        """Transform the meshdata, center and zero position by given Matrix

        :param transformation: 4x4 homogeneous transformation matrix
        """

        if self._vertices is not None:
            transformed_vertices = transformVertices(self._vertices, transformation)
            transformed_normals = transformNormals(self._normals, transformation) if self._normals is not None else None

            transformation_matrix = transformation.getTransposed()
            if self._center_position is not None:
                center_position = self._center_position.multiply(transformation_matrix)
            else:
                center_position = Reuse
            zero_position = self._zero_position.multiply(transformation_matrix)

            return self.set(vertices=transformed_vertices, normals=transformed_normals, center_position=center_position, zero_position=zero_position)
        else:
            return MeshData(vertices = self._vertices)

    def getExtents(self, matrix: Optional[Matrix] = None) -> Optional[AxisAlignedBox]:
        """Get the extents of this mesh.

        :param matrix: The transformation matrix from model to world coordinates.
        """

        if self._vertices is None:
            return None

        if matrix is not None:
            data = self.getConvexHullTransformedVertices(matrix)
        else:
            data = self.getConvexHullVertices()

        if data is None:
            return None

        min = data.min(axis=0)
        max = data.max(axis=0)

        return AxisAlignedBox(minimum=Vector(min[0], min[1], min[2]), maximum=Vector(max[0], max[1], max[2]))

    def getVerticesAsByteArray(self) -> Optional[bytes]:
        """Get all vertices of this mesh as a bytearray

        :return: A bytearray object with 3 floats per vertex.
        """

        if self._vertices is None:
            return None
        return self._vertices.tostring()

    def getNormalsAsByteArray(self) -> Optional[bytes]:
        """Get all normals of this mesh as a bytearray

        :return: A bytearray object with 3 floats per normal.
        """

        if self._normals is None:
            return None
        return self._normals.tostring()

    def getIndicesAsByteArray(self) -> Optional[bytes]:
        """Get all indices as a bytearray

        :return: A bytearray object with 3 ints per face.
        """

        if self._indices is None:
            return None
        return self._indices.tostring()

    def getColorsAsByteArray(self) -> Optional[bytes]:
        if self._colors is None:
            return None
        return self._colors.tostring()

    def getUVCoordinatesAsByteArray(self) -> Optional[bytes]:
        if self._uvs is None:
            return None
        return self._uvs.tostring()

    def _computeConvexHull(self) -> None:
        """Convex hull handling"""

        points = self.getVertices()
        if points is None:
            return
        self._convex_hull = approximateConvexHull(points, MAXIMUM_HULL_VERTICES_COUNT)

    def getConvexHull(self) -> Optional[scipy.spatial.ConvexHull]:
        """Gets the Convex Hull of this mesh

        :return: :type{scipy.spatial.ConvexHull}
        """

        with self._convex_hull_lock:
            if self._convex_hull is None:
                self._computeConvexHull()
            return self._convex_hull

    def getConvexHullVertices(self) -> Optional[numpy.ndarray]:
        """Gets the convex hull points

        :return: :type{numpy.ndarray} the vertices which describe the convex hull
        """

        if self._convex_hull_vertices is None:
            convex_hull = self.getConvexHull()
            if convex_hull is None:
                return None
            self._convex_hull_vertices = numpy.take(convex_hull.points, convex_hull.vertices, axis=0)
        return self._convex_hull_vertices

    def getConvexHullTransformedVertices(self, transformation: Matrix) -> Optional[numpy.ndarray]:
        """Gets transformed convex hull points

        :return: :type{numpy.ndarray} the vertices which describe the convex hull
        """

        vertices = self.getConvexHullVertices()
        if vertices is not None:
            return transformVertices(vertices, transformation)
        else:
            return None

    def getFacePlane(self, face_id: int) -> Tuple[numpy.ndarray, numpy.ndarray]:
        """Gets the plane the supplied face lies in. The resultant plane is specified by a point and a normal.

        :param face_id: :type{int} The index of the face (not the flattened indices).
        :return: :type{Tuple[numpy.ndarray, numpy.ndarray]} A plane, the 1st vector is the center, the 2nd the normal.
        """

        v_a, v_b, v_c = self.getFaceNodes(face_id)
        in_point = (v_a + v_b + v_c) / 3.0
        face_normal = numpy.cross(v_b - v_a, v_c - v_a)
        return in_point, face_normal

    def getFaceNodes(self, face_id: int) -> Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]:
        """Gets the node vectors of the supplied face.

        :param face_id: :type{int} The index of the face (not the flattened indices).
        :return: :type{Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]} Tuple of all three local vectors. 
        """

        if self._indices is None or len(self._indices) == 0:
            base_index = face_id * 3
            v_a = self._vertices[base_index]
            v_b = self._vertices[base_index + 1]
            v_c = self._vertices[base_index + 2]
        else:
            v_a = self._vertices[self._indices[face_id][0]]
            v_b = self._vertices[self._indices[face_id][1]]
            v_c = self._vertices[self._indices[face_id][2]]
        return v_a, v_b, v_c

    def hasAttribute(self, key: str) -> bool:
        return key in self._attributes

    def getAttribute(self, key: str):
        """the return value is a dict with at least keys opengl_name, opengl_type, value"""

        return self._attributes[key]

    def attributeNames(self) -> List[str]:
        """Return attribute names in alphabetical order

        The sorting assures that the order is always the same.
        """
        if not self._attributes:
            return []

        result = list(self._attributes.keys())
        result.sort()
        return result

    def invertNormals(self) -> None:
        if self._normals is not None:
            mirror = Matrix()
            mirror.setToIdentity()
            mirror.scaleByFactor(-1.0)
            self._normals = transformNormals(self._normals, mirror)
        if self._indices is not None:
            new_indices = []
            for face in self._indices:
                new_indices.append([face[1], face[0], face[2]])
            self._indices = NumPyUtil.immutableNDArray(new_indices)
            self._indices_byte_array = None
        else:
            new_vertices = []
            num_vertices = len(self._vertices)
            for i in range(0, num_vertices, 3):
                new_vertices.append(self._vertices[i + 1])
                new_vertices.append(self._vertices[i])
                new_vertices.append(self._vertices[i + 2])
            self._vertices = NumPyUtil.immutableNDArray(new_vertices)

    def toString(self) -> str:
        return "MeshData(_vertices=" + str(self._vertices) + ", _normals=" + str(self._normals) + ", _indices=" + \
               str(self._indices) + ", _colors=" + str(self._colors) + ", _uvs=" + str(self._uvs) + ", _attributes=" + \
               str(self._attributes.keys()) + ") "


def transformVertices(vertices: numpy.ndarray, transformation: Matrix) -> numpy.ndarray:
    """Transform an array of vertices using a matrix

    :param vertices: :type{numpy.ndarray} array of 3D vertices
    :param transformation: a 4x4 matrix
    :return: :type{numpy.ndarray} the transformed vertices
    """

    data = numpy.pad(vertices, ((0, 0), (0, 1)), "constant", constant_values=(0.0, 0.0))
    data = data.dot(transformation.getTransposed().getData())
    data += transformation.getData()[:, 3]
    data = data[:, 0:3]
    return data


def transformNormals(normals: numpy.ndarray, transformation: Matrix) -> numpy.ndarray:
    """Transform an array of normals using a matrix

    :param normals: :type{numpy.ndarray} array of 3D normals
    :param transformation: a 4x4 matrix
    :return: :type{numpy.ndarray} the transformed normals

    :note This assumes the normals are untranslated unit normals, and returns the same.
    """

    data = numpy.pad(normals, ((0, 0), (0, 1)), "constant", constant_values=(0.0, 0.0))

    # Get the translation from the transformation so we can cancel it later.
    translation = transformation.getTranslation()

    # Transform the normals so they get the proper rotation
    data = data.dot(transformation.getTransposed().getData())
    data += transformation.getData()[:, 3]
    data = data[:, 0:3]

    # Cancel the translation since normals should always go from origin to a point on the unit sphere.
    data[:] -= translation.getData()

    # Re-normalize the normals, since the transformation can contain scaling.
    lengths = numpy.linalg.norm(data, axis = 1)
    lengths[lengths == 0] = 1
    data[:, 0] /= lengths
    data[:, 1] /= lengths
    data[:, 2] /= lengths

    return data


def roundVertexArray(vertices: numpy.ndarray, unit: float) -> numpy.ndarray:
    """Round an array of vertices off to the nearest multiple of unit

    :param vertices: :type{numpy.ndarray} the source array of vertices
    :param unit: :type{float} the unit to scale the vertices to
    :return: :type{numpy.ndarray} the rounded vertices
    """

    expanded = vertices / unit
    rounded = expanded.round(0)
    return rounded * unit


def uniqueVertices(vertices: numpy.ndarray) -> numpy.ndarray:
    """Extract the unique vectors from an array of vectors

    :param vertices: :type{numpy.ndarray} the source array of vertices
    :return: :type{numpy.ndarray} the array of unique vertices
    """

    vertex_byte_view = numpy.ascontiguousarray(vertices).view(
        numpy.dtype((numpy.void, vertices.dtype.itemsize * vertices.shape[1])))
    _, idx = numpy.unique(vertex_byte_view, return_index=True)
    return vertices[idx]  # Select the unique rows by index.


def approximateConvexHull(vertex_data: numpy.ndarray, target_count: int) -> Optional[scipy.spatial.ConvexHull]:
    """Compute an approximation of the convex hull of an array of vertices

    :param vertices: :type{numpy.ndarray} the source array of vertices
    :param target_count: :type{int} the maximum number of vertices which may be in the result
    :return: :type{scipy.spatial.ConvexHull} the convex hull or None if the input was degenerate
    """

    start_time = time()

    input_max = target_count * 50   # Maximum number of vertices we want to feed to the convex hull algorithm.
    unit_size = 0.0125             # Initial rounding interval. i.e. round to 0.125.
    max_unit_size = 0.01

    # Round off vertices and extract the uniques until the number of vertices is below the input_max.
    while len(vertex_data) > input_max and unit_size <= max_unit_size:
        new_vertex_data = uniqueVertices(roundVertexArray(vertex_data, unit_size))
        # Check if there is variance in Z value, we need it for the convex hull calculation
        if numpy.amin(new_vertex_data[:, 1]) != numpy.amax(new_vertex_data[:, 1]):
            vertex_data = new_vertex_data
        else:
            # Prevent convex hull calculation from crashing
            Logger.log("w", "Stopped shrinking data because otherwise the convex hull calculation will crash. Vertices: %s (target: %s)" % (len(vertex_data), input_max))
            break
        unit_size *= 2

    if len(vertex_data) < 4:
        return None

    # Take the convex hull and keep on rounding it off until the number of vertices is below the target_count.
    hull_result = createConvexHull(vertex_data)
    vertex_data = numpy.take(hull_result.points, hull_result.vertices, axis=0)

    while len(vertex_data) > target_count and unit_size <= max_unit_size:
        vertex_data = uniqueVertices(roundVertexArray(vertex_data, unit_size))
        hull_result = createConvexHull(vertex_data)
        vertex_data = numpy.take(hull_result.points, hull_result.vertices, axis=0)
        unit_size *= 2

    end_time = time()
    Logger.log("d", "approximateConvexHull(target_count=%s) Calculating 3D convex hull took %s seconds. %s input vertices. %s output vertices.",
               target_count, end_time - start_time, len(vertex_data), len(hull_result.vertices))
    return hull_result


def createConvexHull(vertex_data: numpy.ndarray) -> scipy.spatial.ConvexHull:
    try:
        hull_result = scipy.spatial.ConvexHull(vertex_data)
    except scipy.spatial.qhull.QhullError:
        # Can get an error when the model is lower dimensional, use "QJ" is make it full dimensional
        Logger.log("w", "Loaded model is low-dimensional, apply QJ to make it full dimensional")
        hull_result = scipy.spatial.ConvexHull(vertex_data, qhull_options="QJ")
    return hull_result


def calculateNormalsFromVertices(vertices: numpy.ndarray, vertex_count: int) -> numpy.ndarray:
    """Calculate the normals of this mesh, assuming it was created by using addFace (eg; the verts are connected)

    :param vertices: :type{narray} list of vertices as a 1D list of float triples
    :param vertex_count: :type{integer} the number of vertices to use in the vertices array
    :return: :type{narray} list normals as a 1D array of floats, each group of 3 floats is a vector
    """

    start_time = time()
    # Numpy magic!

    # Old way of doing it, assuming that each face has 3 unique verts
    # Then, take the cross product of each pair of vectors formed from a set of three vertices.
    # The [] operator on a numpy array returns itself a numpy array. The slicing syntax is [begin:end:step],
    # so in this case we perform the cross over a two arrays. The first array is built from the difference
    # between every second item in the array starting at two and every third item in the array starting at
    # zero. The second array is built from the difference between every third item in the array starting at
    # two and every third item in the array starting at zero. The cross operation then returns an array of
    # the normals of each set of three vertices.
    n = numpy.cross(vertices[1:vertex_count:3] - vertices[:vertex_count:3],
                    vertices[2:vertex_count:3] - vertices[:vertex_count:3])
    # We then calculate the length for each normal and perform normalization on the normals.
    l = numpy.linalg.norm(n, axis = 1)
    l[l == 0] = 1  # Prevent division by 0. These normals are lost, but if the normal is 0-length then the triangle won't be visible anyway.
    n[:, 0] /= l
    n[:, 1] /= l
    n[:, 2] /= l
    # Finally, we store the normals per vertex, with each face normal being repeated three times, once for
    # every vertex.
    normals = n.repeat(3, axis = 0)

    end_time = time()
    Logger.log("d", "Calculating normals took %s seconds", end_time - start_time)
    return normals


def calculateNormalsFromIndexedVertices(vertices: numpy.ndarray, indices: numpy.ndarray, face_count: int) -> numpy.ndarray:
    """Calculate the normals of this mesh of triagles using indexes.

    :param vertices: :type{narray} list of vertices as a 1D list of float triples
    :param indices: :type{narray} list of indices as a 1D list of integers
    :param face_count: :type{integer} the number of triangles defined by the indices array
    :return: :type{narray} list normals as a 1D array of floats, each group of 3 floats is a vector
    """

    start_time = time()
    # Numpy magic!
    # First, reset the normals
    normals = numpy.zeros((face_count*3, 3), dtype=numpy.float32)

    for face in indices[0:face_count]:
        normals[face[0]] = numpy.cross(vertices[face[0]] - vertices[face[1]], vertices[face[0]] - vertices[face[2]])
        length = numpy.linalg.norm(normals[face[0]])
        normals[face[0]] /= length
        normals[face[1]] = normals[face[0]]
        normals[face[2]] = normals[face[0]]
    end_time = time()
    Logger.log("d", "Calculating normals took %s seconds", end_time - start_time)
    return normals
