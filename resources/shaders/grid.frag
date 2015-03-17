uniform lowp vec4 u_gridColor0;
uniform lowp vec4 u_gridColor1;

varying lowp vec4 v_color;
varying highp vec2 v_uvs;


void main()
{
	if (mod(floor(v_uvs.x / 10.0) - floor(v_uvs.y / 10.0), 2.0) < 1.0)
		gl_FragColor = u_gridColor0;
	else
		gl_FragColor = u_gridColor1;
}
