[shaders]
vertex =
    uniform highp mat4 u_modelMatrix;
    uniform highp mat4 u_viewMatrix;
    uniform highp mat4 u_projectionMatrix;

    attribute highp vec4 a_vertex;

    void main()
    {
        gl_Position = u_projectionMatrix * u_viewMatrix * u_modelMatrix * a_vertex;
    }

fragment =
    uniform lowp vec4 u_color;

    void main()
    {
        gl_FragColor = u_color;

        gl_FragColor.r += ( gl_PrimitiveID           % 0x10) / 255.;
        gl_FragColor.g += ((gl_PrimitiveID /   0x10) % 0x10) / 255.;
        gl_FragColor.b += ((gl_PrimitiveID /  0x100) % 0x10) / 255.;
        gl_FragColor.a += ((gl_PrimitiveID / 0x1000) % 0x10) / 255.;
    }

vertex41core =
    #version 410
    uniform highp mat4 u_modelMatrix;
    uniform highp mat4 u_viewMatrix;
    uniform highp mat4 u_projectionMatrix;

    in highp vec4 a_vertex;

    void main()
    {
        gl_Position = u_projectionMatrix * u_viewMatrix * u_modelMatrix * a_vertex;
    }

fragment41core =
    #version 410
    uniform lowp vec4 u_color;
    out vec4 frag_color;

    void main()
    {
        frag_color = u_color;

        frag_color.r += ( gl_PrimitiveID           % 0x10) / 255.;
        frag_color.g += ((gl_PrimitiveID /   0x10) % 0x10) / 255.;
        frag_color.b += ((gl_PrimitiveID /  0x100) % 0x10) / 255.;
        frag_color.a += ((gl_PrimitiveID / 0x1000) % 0x10) / 255.;
    }

[defaults]

[bindings]
u_modelMatrix = model_matrix
u_viewMatrix = view_matrix
u_projectionMatrix = projection_matrix
u_color = selection_color

[attributes]
a_vertex = vertex
a_color = color
