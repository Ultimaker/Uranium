# Copyright (c) 2015 Ultimaker B.V.
# Copyright (c) 2013 David Braam
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Mesh.MeshReader import MeshReader
from UM.Mesh.MeshData import MeshData
from UM.Logger import Logger
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector
from UM.Scene.SceneNode import SceneNode
from UM.Job import Job

import os
import struct
import math
import time

class STLReader(MeshReader):
    def __init__(self):
        super(STLReader, self).__init__()
        self._supported_extensions = [".stl"]

    ## Decide if we need to use ascii or binary in order to read file
    def read(self, file_name):
        mesh = None
        scene_node = None

        mesh = MeshData()
        scene_node = SceneNode()
        f = open(file_name, "rb")
        if not self._loadBinary(mesh, f):
            f.close()
            f = open(file_name, "rt")
            try:
                self._loadAscii(mesh, f)
            except UnicodeDecodeError:
                pass
            f.close()

        f.close()
        time.sleep(0.1) #Yield somewhat to ensure the GUI has time to update a bit.
        mesh.calculateNormals(fast = True)

        Logger.log("d", "Loaded a mesh with %s vertices", mesh.getVertexCount())
        scene_node.setMeshData(mesh)
        return scene_node

    # Private
    ## Load the STL data from file by consdering the data as ascii.
    # \param mesh The MeshData object where the data is written to.
    # \param f The file handle
    def _loadAscii(self, mesh, f):
        num_verts = 0
        for lines in f:
            for line in lines.split("\r"):
                if "vertex" in line:
                    num_verts += 1

        mesh.reserveFaceCount(num_verts / 3)
        f.seek(0, os.SEEK_SET)
        vertex = 0
        face = [None, None, None]
        for lines in f:
            for line in lines.split("\r"):
                if "vertex" in line:
                    face[vertex] = line.split()[1:]
                    vertex += 1
                    if vertex == 3:
                        mesh.addFace(
                            float(face[0][0]), float(face[0][2]), -float(face[0][1]),
                            float(face[1][0]), float(face[1][2]), -float(face[1][1]),
                            float(face[2][0]), float(face[2][2]), -float(face[2][1])
                        )
                        vertex = 0

                Job.yieldThread()

    # Private
    ## Load the STL data from file by consdering the data as Binary.
    # \param mesh The MeshData object where the data is written to.
    # \param f The file handle
    def _loadBinary(self, mesh, f):
        f.read(80) #Skip the header
        
        num_faces = struct.unpack("<I", f.read(4))[0]
        # On ascii files, the num_faces will be big, due to 4 ascii bytes being seen as an unsigned int.
        if num_faces < 1 or num_faces > 1000000000:
            return False
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        f.seek(84, os.SEEK_SET)
        if file_size < num_faces * 50 + 84:
            return False

        mesh.reserveFaceCount(num_faces)
        for idx in range(0, num_faces):
            data = struct.unpack(b"<ffffffffffffH", f.read(50))
            mesh.addFace(
                data[3], data[5], -data[4],
                data[6], data[8], -data[7],
                data[9], data[11], -data[10]
            )
            Job.yieldThread()

        return True
