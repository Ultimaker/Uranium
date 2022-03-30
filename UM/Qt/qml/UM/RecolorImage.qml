// Copyright (c) 2018 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import UM 1.3 as UM

Item
{
    id: base;

    property alias source: img.source
    property alias color: shader.color
    property alias sourceSize: img.sourceSize

    Image
    {
        id: img
        anchors.fill: parent
        visible: false
        sourceSize.width: parent.width
        sourceSize.height: parent.height
    }

    ShaderEffect
    {
        id: shader
        anchors.fill: parent

        property variant src: img
        property color color: "#fff"

        vertexShader: Resources.getPath(Resources.Shaders, "recolor_image.vert.qsb")
        fragmentShader: Resources.getPath(Resources.Shaders, "recolor_image.frag.qsb")
    }
}
