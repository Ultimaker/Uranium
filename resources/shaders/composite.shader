[shaders]
vertex =
    uniform highp mat4 u_modelViewProjectionMatrix;
    attribute highp vec4 a_vertex;
    attribute highp vec2 a_uvs;

    varying highp vec2 v_uvs;

    void main()
    {
        gl_Position = u_modelViewProjectionMatrix * a_vertex;
        v_uvs = a_uvs;
    }

fragment =
    uniform sampler2D u_layers[8];
    uniform int u_layer_count;

    varying vec2 v_uvs;

    void main()
    {
        mediump vec4 result = vec4(0.0);
        for(int i = 0; i < u_layer_count; ++i)
        {
            result += texture2D(u_layers[i], v_uvs);
        }
        gl_FragColor = result;
    }

[defaults]

[bindings]
u_modelViewProjectionMatrix = model_view_projection_matrix

[attributes]
a_vertex = vertex
a_uvs = uv
