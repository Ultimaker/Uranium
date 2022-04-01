#version 440
layout(location = 0) in vec2 coord;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec4 color;
};
layout(binding = 1) uniform sampler2D src;
void main() {
    vec4 tex = texture(src, coord);
    float alpha = tex.a  * qt_Opacity;
    fragColor = vec4(color.r * alpha, color.g * alpha, color.b * alpha, alpha);
}
