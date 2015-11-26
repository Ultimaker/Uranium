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
        mediump vec4 result = vec4(0.0);

        result += texture2D(u_layer0, v_uvs);
        result += texture2D(u_layer1, v_uvs);
        result += texture2D(u_layer2, v_uvs);
        result += texture2D(u_layer3, v_uvs);

        //gl_FragColor = result;
        gl_FragColor = vec4(v_uvs.x, v_uvs.y, 0.0, 1.0);
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
