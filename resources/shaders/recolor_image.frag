#version 420
layout(location = 0) in highp vec2 coord;
layout(std140, binding = 0) uniform buf {
    vec4 color;
    float qt_Opacity;
};
layout(binding=1) uniform sampler2D src;
layout(location = 0) out vec4 frag_color;
void main() {
    lowp vec4 tex = texture(src, coord);
    lowp float alpha = tex.a  * qt_Opacity;
    frag_color = vec4(color.r * alpha, color.g * alpha, color.b * alpha, alpha);
}
