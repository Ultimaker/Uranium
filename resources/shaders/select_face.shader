[shaders]
vertex =
    // NOTE: These legacy shaders are compiled, but not used. Select-by-face isn't possible in legacy-render-mode.
    uniform highp mat4 u_modelMatrix;
    uniform highp mat4 u_viewMatrix;
    uniform highp mat4 u_projectionMatrix;
    uniform highp int u_modelId;

    attribute highp vec4 a_vertex;

    void main()
    {
        gl_Position = u_projectionMatrix * u_viewMatrix * u_modelMatrix * a_vertex;
    }

fragment =
    // NOTE: These legacy shaders are compiled, but not used. Select-by-face isn't possible in legacy-render-mode.

    void main()
    {
        gl_FragColor = vec4(0., 0., 0., 1.);
        // NOTE: Select face can't be used in compatibility-mode;
        //       the __VERSION__ macro may give back the max the graphics driver supports,
        //       rather than the one supported by the selected OpenGL version.
    }

vertex41core =
    #version 410

    uniform highp mat4 u_modelMatrix;
    uniform highp mat4 u_viewMatrix;
    uniform highp mat4 u_projectionMatrix;
    uniform highp int u_modelId;

    in highp vec4 a_vertex;

    flat out highp int v_modelId;

    void main()
    {
        gl_Position = u_projectionMatrix * u_viewMatrix * u_modelMatrix * a_vertex;
        v_modelId = u_modelId;
    }

fragment41core =
    #version 410

    flat in highp int v_modelId;

    out vec4 frag_color;

    void main()
    {
        frag_color.r = (gl_PrimitiveID & 0xff) / 255.;
        frag_color.g = ((gl_PrimitiveID >> 8) & 0xff) / 255.;
        frag_color.b = ((gl_PrimitiveID >> 16) & 0xff) / 255.;
        frag_color.a = (255 - v_modelId) / 255.; // Invert to ease visualization in images, and so that 0 means no object
    }

[defaults]

[bindings]
u_modelMatrix = model_matrix
u_viewMatrix = view_matrix
u_projectionMatrix = projection_matrix
u_modelId = model_id

[attributes]
a_vertex = vertex
