[shaders]
vertex =
    uniform highp mat4 u_modelViewProjectionMatrix;
    attribute highp vec4 a_vertex;
    attribute lowp vec4 a_color;
    varying lowp vec4 v_color;
    void main()
    {
        gl_Position = u_modelViewProjectionMatrix * a_vertex;
        v_color = a_color;
    }

fragment =
    varying lowp vec4 v_color;
    void main()
    {
        gl_FragColor = v_color;
    }

[defaults]

[bindings]
u_modelViewProjectionMatrix = model_view_projection_matrix

[attributes]
a_vertex = vertex
a_color = color
