// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import UM 1.3 as UM

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

        vertexShader: UM.OpenGLContextProxy.isLegacyOpenGL ?
            "
            uniform highp mat4 qt_Matrix;
            attribute highp vec4 qt_Vertex;
            attribute highp vec2 qt_MultiTexCoord0;
            varying highp vec2 coord;
            void main() {
                coord = qt_MultiTexCoord0;
                gl_Position = qt_Matrix * qt_Vertex;
            }
            " : "
            #version 410
            uniform highp mat4 qt_Matrix;
            in highp vec4 qt_Vertex;
            in highp vec2 qt_MultiTexCoord0;
            out highp vec2 coord;
            void main() {
                coord = qt_MultiTexCoord0;
                gl_Position = qt_Matrix * qt_Vertex;
            }
            "

        fragmentShader: UM.OpenGLContextProxy.isLegacyOpenGL ?
            "
            varying highp vec2 coord;
            uniform sampler2D src;
            uniform lowp vec4 color;
            uniform lowp float qt_Opacity;
            void main() {
                lowp vec4 tex = texture2D(src, coord);
                lowp float alpha = tex.a  * qt_Opacity;
                gl_FragColor = vec4(color.r * alpha, color.g * alpha, color.b * alpha, alpha);
            }
            " : "
            #version 410
            in highp vec2 coord;
            uniform sampler2D src;
            uniform lowp vec4 color;
            uniform lowp float qt_Opacity;
            out vec4 frag_color;
            void main() {
                lowp vec4 tex = texture(src, coord);
                lowp float alpha = tex.a  * qt_Opacity;
                frag_color = vec4(color.r * alpha, color.g * alpha, color.b * alpha, alpha);
            }
            "
    }
}
