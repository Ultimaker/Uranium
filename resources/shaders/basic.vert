uniform highp mat4 u_modelMatrix;
uniform highp mat4 u_viewMatrix;
uniform highp mat4 u_projectionMatrix;

attribute highp vec4 a_vertex;
attribute lowp vec4 a_color;

varying lowp vec4 v_color;

void main()
{
    gl_Position = u_projectionMatrix * u_viewMatrix * u_modelMatrix * a_vertex;
    v_color = a_color;
}
