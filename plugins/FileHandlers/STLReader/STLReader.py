# Copyright (c) 2020 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import platform
import struct

import numpy

from UM.Job import Job
from UM.Logger import Logger
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshReader import MeshReader
from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType
from UM.Scene.SceneNode import SceneNode

use_numpystl = False

try:
    # Work around for CURA-7154. Some models crash with a segfault, but only when packed.
    if platform.system() != "Linux":
        import stl  # numpy-stl lib
        import stl.mesh

        # Increase max count. (100 million should be okay-ish)
        stl.stl.MAX_COUNT = 100000000
        use_numpystl = True
    else:
        Logger.log("w", "Not loading numpy-stl due to linux issue")
except ImportError:
    Logger.log("w", "Could not find numpy-stl, falling back to slower code.")
    # We have our own fallback code.


class STLReader(MeshReader):
    def __init__(self) -> None:
        super().__init__()

        MimeTypeDatabase.addMimeType(
            MimeType(
                name = "model/stl",
                comment = "Uranium STL File",
                suffixes = ["stl"]
            )
        )
        self._supported_extensions = [".stl"]

    def load_file(self, file_name, mesh_builder, _use_numpystl = False):
        file_read = False
        if _use_numpystl:
            Logger.log("i", "Using NumPy-STL to load STL data.")
            try:
                self._loadWithNumpySTL(file_name, mesh_builder)
                file_read = True
            except:
                Logger.logException("e", "Reading file failed with Numpy-STL!")

        if not file_read:
            Logger.log("i", "Using legacy code to load STL data.")
            f = open(file_name, "rb")
            if not self._loadBinary(mesh_builder, f):
                f.close()
                f = open(file_name, "rt", encoding = "utf-8")
                try:
                    self._loadAscii(mesh_builder, f)
                except UnicodeDecodeError:
                    return None
                f.close()
            Job.yieldThread()  # Yield somewhat to ensure the GUI has time to update a bit.

        mesh_builder.calculateNormals(fast = True)
        mesh_builder.setFileName(file_name)

    def _read(self, file_name):
        """Decide if we need to use ascii or binary in order to read file"""

        mesh_builder = MeshBuilder()
        scene_node = SceneNode()

        self.load_file(file_name, mesh_builder, _use_numpystl = use_numpystl)

        mesh = mesh_builder.build()

        if use_numpystl:
            verts = mesh.getVertices()
            # In some cases numpy stl reads incorrectly and the result is that the Z values are all 0
            # Add new error cases if you find them.
            if numpy.amin(verts[:, 1]) == numpy.amax(verts[:, 1]):
                # Something may have gone wrong in numpy stl, start over without numpy stl
                Logger.log("w", "All Z coordinates are the same using numpystl, trying again without numpy stl.")
                mesh_builder = MeshBuilder()
                self.load_file(file_name, mesh_builder, _use_numpystl = False)
                mesh = mesh_builder.build()

                verts = mesh.getVertices()
                if numpy.amin(verts[:, 1]) == numpy.amax(verts[:, 1]):
                    Logger.log("e", "All Z coordinates are still the same without numpy stl... let's hope for the best")

        if mesh_builder.getVertexCount() == 0:
            Logger.log("d", "File did not contain valid data, unable to read.")
            return None  # We didn't load anything.
        scene_node.setMeshData(mesh)
        Logger.log("d", "Loaded a mesh with %s vertices", mesh_builder.getVertexCount())

        return scene_node

    def _swapColumns(self, array, frm, to):
        array[:, [frm, to]] = array[:, [to, frm]]

    def _loadWithNumpySTL(self, file_name, mesh_builder):
        for loaded_data in stl.mesh.Mesh.from_multi_file(file_name, mode=stl.stl.Mode.AUTOMATIC):
            vertices = numpy.resize(loaded_data.points.flatten(), (int(loaded_data.points.size / 3), 3))

            # Invert values of second column
            vertices[:, 1] *= -1

            # Swap column 1 and 2 (We have a different coordinate system)
            self._swapColumns(vertices, 1, 2)

            mesh_builder.addVertices(vertices)

    # Private
    def _loadAscii(self, mesh_builder, f):
        """Load the STL data from file by considering the data as ascii.

        :param mesh_builder: The MeshData object where the data is written to.
        :param f: The file handle
        """

        num_verts = 0
        for lines in f:
            for line in lines.split("\r"):
                if "vertex" in line:
                    num_verts += 1

        mesh_builder.reserveFaceCount(num_verts / 3)
        f.seek(0, os.SEEK_SET)
        vertex = 0
        face = [None, None, None]
        for lines in f:
            for line in lines.split("\r"):
                if "vertex" in line:
                    face[vertex] = line.split()[1:]
                    vertex += 1
                    if vertex == 3:
                        mesh_builder.addFaceByPoints(
                            float(face[0][0]), float(face[0][2]), -float(face[0][1]),
                            float(face[1][0]), float(face[1][2]), -float(face[1][1]),
                            float(face[2][0]), float(face[2][2]), -float(face[2][1])
                        )
                        vertex = 0

                Job.yieldThread()

    # Private
    def _loadBinary(self, mesh_builder, f):
        """Load the STL data from file by consdering the data as Binary.
        :param mesh: The MeshData object where the data is written to.
        :param f: The file handle
        """

        f.read(80)  # Skip the header

        try:
            num_faces = struct.unpack("<I", f.read(4))[0]
        except struct.error:  # Can't unpack it if the file didn't have 4 bytes in it.
            return False
        # On ascii files, the num_faces will be big, due to 4 ascii bytes being seen as an unsigned int.
        if num_faces < 1 or num_faces > 1000000000:
            return False
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        f.seek(84, os.SEEK_SET)
        if file_size < num_faces * 50 + 84:
            return False

        mesh_builder.reserveFaceCount(num_faces)
        for idx in range(0, num_faces):
            data = struct.unpack(b"<ffffffffffffH", f.read(50))
            mesh_builder.addFaceByPoints(
                data[3], data[5], -data[4],
                data[6], data[8], -data[7],
                data[9], data[11], -data[10]
            )
            Job.yieldThread()

        return True
