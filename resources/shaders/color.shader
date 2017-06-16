[shaders]
vertex =
    uniform highp mat4 u_modelViewProjectionMatrix;

    attribute highp vec4 a_vertex; //Vertex coordinate.
    void main()
    {
        gl_Position = u_modelViewProjectionMatrix * a_vertex; //Transform the vertex coordinates with the model view projection.
    }

fragment =
    uniform lowp vec4 u_color;

    void main()
    {
        gl_FragColor = u_color; //Always use the uniform colour. The entire mesh will be the same colour.
    }

[defaults]
u_color = [0.5, 0.5, 0.5, 1.0]

[bindings]
u_modelViewProjectionMatrix = model_view_projection_matrix

[attributes]
a_vertex = vertex
