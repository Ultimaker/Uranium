uniform mat4 u_modelMatrix;
uniform mat4 u_viewMatrix;
uniform mat4 u_projectionMatrix;

attribute vec4 a_vertex;
attribute vec4 a_normal;

varying vec3 v_vertex;
varying vec3 v_normal;

void main()
{
    gl_Position = u_projectionMatrix * u_viewMatrix * u_modelMatrix * a_vertex;
    v_vertex = (u_modelMatrix * a_vertex).xyz;
    v_normal = (u_modelMatrix * a_normal).xyz;
}
