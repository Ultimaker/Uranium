uniform lowp vec4 u_disabledColor;
uniform lowp vec4 u_activeColor;

varying lowp vec4 v_color;

void main()
{
    if(u_activeColor == v_color)
    {
        gl_FragColor = v_color;
    }
    else
    {
        gl_FragColor = u_disabledColor;
    }
}
