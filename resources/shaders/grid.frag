uniform lowp vec4 u_gridColor0;
uniform lowp vec4 u_gridColor1;

varying lowp vec4 v_color;
varying highp vec2 v_uvs;


void main()
{
//     gl_FragColor = v_color;
    gl_FragColor = vec4(v_uvs.x, v_uvs.y, 0.0, 1.0);
}
