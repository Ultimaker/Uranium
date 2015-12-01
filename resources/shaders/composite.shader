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
    uniform sampler2D u_layer0;
    uniform sampler2D u_layer1;
    uniform sampler2D u_layer2;
    uniform sampler2D u_layer3;

    varying vec2 v_uvs;

    void main()
    {
        vec4 result = vec4(0.95, 0.95, 0.95, 1.0);
        vec4 layer0 = texture2D(u_layer0, v_uvs);
        vec4 layer1 = vec4(texture2D(u_layer1, v_uvs).a);
        gl_FragColor = mix(result, layer0, layer0.a);
    }

[defaults]
u_layer0 = 0
u_layer1 = 1
u_layer2 = 2
u_layer3 = 3

[bindings]

[attributes]
a_vertex = vertex
a_uvs = uv
