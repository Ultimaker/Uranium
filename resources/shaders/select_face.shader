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
    uniform highp int u_maxModelId;  // So the output can still be up to ~8M faces for an ungrouped object.

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

    uniform highp int u_maxModelId;  // So the output can still be up to ~8M faces for an ungrouped object.
    flat in highp int v_modelId;

    out vec4 frag_color;

    void main()
    {
        int max_model_adjusted = int(exp2(int(ceil(log2(u_maxModelId))) + 1));
        int blue_part_face_id = (gl_PrimitiveID / 0x10000) % 0x80;

        frag_color = vec4(0., 0., 0., 1.);
        frag_color.r = (gl_PrimitiveID % 0x100) / 255.;
        frag_color.g = ((gl_PrimitiveID / 0x100) % 0x100) / 255.;
        frag_color.b = (0x1 + 2 * v_modelId + max_model_adjusted * blue_part_face_id) / 255.;

        // Don't use alpha for anything, as some faces may be behind others, an only the front one's value is desired.
        // There isn't any control over the background color, so a signal-bit is put into the blue byte.
    }

[defaults]

[bindings]
u_modelMatrix = model_matrix
u_viewMatrix = view_matrix
u_projectionMatrix = projection_matrix
u_modelId = model_id
u_maxModelId = max_model_id

[attributes]
a_vertex = vertex
