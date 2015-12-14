[shaders]
vertex =
    uniform highp mat4 u_modelViewProjectionMatrix;

    attribute highp vec4 a_vertex;

    void main()
    {
        gl_Position = u_modelViewProjectionMatrix * a_vertex;
    }

fragment =
    uniform lowp vec4 u_color;

    void main()
    {
        gl_FragColor = u_color;
    }

[defaults]

[bindings]
u_modelViewProjectionMatrix = model_view_projection_matrix
u_color = selection_color

[attributes]
a_vertex = vertex
a_color = color
