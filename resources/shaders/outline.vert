uniform highp mat4 u_modelMatrix;
uniform highp mat4 u_viewMatrix;
uniform highp mat4 u_projectionMatrix;
uniform highp mat4 u_normalMatrix;

attribute highp vec4 a_vertex;
attribute highp vec4 a_normal;

varying highp vec3 v_vertex;
varying highp vec3 v_normal;
varying highp vec3 v_viewVector;

void main()
{
    vec4 viewspaceVert = u_viewMatrix * u_modelMatrix * a_vertex;
    gl_Position = u_projectionMatrix * viewspaceVert;
    gl_Position.z = 0.0;

    v_vertex = (u_modelMatrix * a_vertex).xyz;
    v_normal = (u_normalMatrix * normalize(a_normal)).xyz;
}
