uniform mediump vec4 u_ambientColor;
uniform mediump vec4 u_diffuseColor;
uniform highp vec3 u_lightPosition;
uniform highp vec3 u_viewPosition;
uniform mediump float u_opacity;
uniform sampler2D u_texture;

varying highp vec3 v_vertex;
varying highp vec3 v_normal;
varying highp vec2 v_uvs;

void main()
{
    mediump vec4 finalColor = vec4(0.0);

    /* Ambient Component */
    finalColor += u_ambientColor;

    highp vec3 normal = normalize(v_normal);
    highp vec3 lightDir = normalize(u_lightPosition - v_vertex);

    /* Diffuse Component */
    highp float NdotL = clamp(dot(normal, lightDir), 0.0, 1.0);
    finalColor += (NdotL * u_diffuseColor);

    finalColor.a = u_opacity;

    vec4 texture = texture2D(u_texture, v_uvs);
    finalColor = mix(finalColor, texture, texture.a);

    gl_FragColor = finalColor;
}
