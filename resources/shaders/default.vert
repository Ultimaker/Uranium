uniform mat4 u_modelMatrix;
uniform mat4 u_viewMatrix;
uniform mat4 u_projectionMatrix;
uniform mat4 u_normalMatrix;

attribute vec4 a_vertex;
attribute vec4 a_normal;

varying vec3 v_vertex;
varying vec3 v_normal;
varying vec3 v_viewVector;

void main()
{
    vec4 viewspaceVert = u_viewMatrix * u_modelMatrix * a_vertex;
    gl_Position = u_projectionMatrix * viewspaceVert;

    v_vertex = (u_modelMatrix * a_vertex).xyz;
    v_normal = (u_normalMatrix * normalize(a_normal)).xyz;
//     v_viewVector = (-viewspaceVert).xyz;
}
