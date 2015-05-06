// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1

Item {
    id: base;

    property alias source: img.source;
    property alias color: shader.color;
    property alias sourceSize: img.sourceSize;

    Image {
        id: img;
        anchors.fill: parent;
        visible: false;
    }

    ShaderEffect {
        id: shader;
        anchors.fill: parent;

        property variant src: img;
        property color color: "#fff";

        vertexShader: "
            uniform highp mat4 qt_Matrix;
            attribute highp vec4 qt_Vertex;
            attribute highp vec2 qt_MultiTexCoord0;
            varying highp vec2 coord;
            void main() {
                coord = qt_MultiTexCoord0;
                gl_Position = qt_Matrix * qt_Vertex;
            }"

        fragmentShader: "
            varying highp vec2 coord;
            uniform sampler2D src;
            uniform lowp vec4 color;
            uniform lowp float qt_Opacity;
            void main() {
                lowp vec4 tex = texture2D(src, coord);
                lowp float alpha = tex.a  * qt_Opacity;
                gl_FragColor = vec4(color.r * alpha, color.g * alpha, color.b * alpha, alpha);
            }"
    }
}
