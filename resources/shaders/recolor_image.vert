#version 420
layout(location = 0) in highp vec4 qt_Vertex;
layout(location = 1) in highp vec2 qt_MultiTexCoord0;
layout(std140, binding = 0) uniform buf {
    highp mat4 qt_Matrix;
};
layout(location = 0) out highp vec2 coord;
void main() {
    coord = qt_MultiTexCoord0;
    gl_Position = qt_Matrix * qt_Vertex;
}
