# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Mesh.MeshWriter import MeshWriter
from UM.Scene.SceneNode import SceneNode
from UM.Scene.Iterator.BreadthFirstIterator import BreadthFirstIterator
from UM.Logger import Logger
from UM.Math.Matrix import Matrix

import xml.etree.ElementTree as ET
import zipfile
import io


class ThreeMFWriter(MeshWriter):
    def __init__(self):
        super().__init__()
        self._namespaces = {
            "3mf": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02",
            "content-types": "http://schemas.openxmlformats.org/package/2006/content-types",
            "relationships": "http://schemas.openxmlformats.org/package/2006/relationships"
        }

    def _convertMatrixToString(self, matrix):
        result = ""
        result += str(matrix._data[0,0]) + " "
        result += str(matrix._data[1,0]) + " "
        result += str(matrix._data[2,0]) + " "
        result += str(matrix._data[0,1]) + " "
        result += str(matrix._data[1,1]) + " "
        result += str(matrix._data[2,1]) + " "
        result += str(matrix._data[0,2]) + " "
        result += str(matrix._data[1,2]) + " "
        result += str(matrix._data[2,2]) + " "
        result += str(matrix._data[0,3]) + " "
        result += str(matrix._data[1,3]) + " "
        result += str(matrix._data[2,3]) + " "
        return result

    def write(self, stream, node, mode = MeshWriter.OutputMode.BinaryMode):
        nodes = []
        for n in BreadthFirstIterator(node):
            if type(n) is not SceneNode or not n.getMeshData():
                continue

            nodes.append(n)
        if not len(nodes):
            return False

        archive = zipfile.ZipFile(stream, "w", compression = zipfile.ZIP_DEFLATED)
        try:
            model_file = zipfile.ZipInfo("3D/3dmodel.model")
            # Because zipfile is stupid and ignores archive-level compression settings when writing with ZipInfo.
            model_file.compress_type = zipfile.ZIP_DEFLATED

            # Create content types file
            content_types_file = zipfile.ZipInfo("[Content_Types].xml")
            content_types_file.compress_type = zipfile.ZIP_DEFLATED
            content_types = ET.Element("Types", xmlns = self._namespaces["content-types"])
            rels_type = ET.SubElement(content_types, "Default", Extension = "rels", ContentType = "application/vnd.openxmlformats-package.relationships+xml")
            model_type = ET.SubElement(content_types, "Default", Extension = "model", ContentType = "application/vnd.ms-package.3dmanufacturing-3dmodel+xml")

            # Create _rels/.rels file
            relations_file = zipfile.ZipInfo("_rels/.rels")
            relations_file.compress_type = zipfile.ZIP_DEFLATED
            relations_element = ET.Element("Relationships", xmlns = self._namespaces["relationships"])
            model_relation_element = ET.SubElement(relations_element, "Relationship", Target = "/3D/3dmodel.model", Id = "rel0", Type = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")

            model = ET.Element('model', unit = "millimeter", xmlns = self._namespaces["3mf"])
            resources = ET.SubElement(model, "resources")
            build = ET.SubElement(model, "build")
            for index, n in enumerate(nodes):
                object = ET.SubElement(resources, "object", id = str(index+1), type = "model")
                mesh = ET.SubElement(object, "mesh")

                mesh_data = n.getMeshData()
                vertices = ET.SubElement(mesh, "vertices")
                verts = mesh_data.getVertices()
                if mesh_data.hasIndices():
                    for face in mesh_data.getIndices():
                        v1 = verts[face[0]]
                        v2 = verts[face[1]]
                        v3 = verts[face[2]]
                        xml_vertex1 = ET.SubElement(vertices, "vertex", x = str(v1[0]), y = str(v1[2]), z = str(v1[1]))
                        xml_vertex2 = ET.SubElement(vertices, "vertex", x = str(v2[0]), y = str(v2[2]), z = str(v2[1]))
                        xml_vertex3 = ET.SubElement(vertices, "vertex", x = str(v3[0]), y = str(v3[2]), z = str(v3[1]))

                    triangles = ET.SubElement(mesh, "triangles")
                    for face in mesh_data.getIndices():
                        triangle = ET.SubElement(triangles, "triangle", v1 = str(face[0]) , v2 = str(face[1]), v3 = str(face[2]))
                else:
                    for vert in verts:
                        xml_vertex = ET.SubElement(vertices, "vertex", x = str(vert[0]), y = str(vert[0]), z = str(vert[0]))

                transformation_string = self._convertMatrixToString(n.getWorldTransformation())
                if transformation_string != self._convertMatrixToString(Matrix()):
                    item = ET.SubElement(build, "item", objectid = str(index+1), transform = transformation_string)
                else:
                    item = ET.SubElement(build, "item", objectid = str(index+1)) #, transform = transformation_string)

            archive.writestr(model_file, b'<?xml version="1.0" encoding="UTF-8"?> \n' + ET.tostring(model))
            archive.writestr(content_types_file, b'<?xml version="1.0" encoding="UTF-8"?> \n' + ET.tostring(content_types))
            archive.writestr(relations_file, b'<?xml version="1.0" encoding="UTF-8"?> \n' + ET.tostring(relations_element))
        except Exception as e:
            Logger.logException("e", "Error writing zip file")
            return False
        finally:
            archive.close()

        return True