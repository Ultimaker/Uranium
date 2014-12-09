uniform mediump vec4 u_ambientColor;
uniform mediump vec4 u_diffuseColor;
uniform mediump vec4 u_specularColor;

uniform highp vec3 u_lightPosition;
uniform mediump vec4 u_lightColor;

uniform mediump float u_shininess;

uniform highp vec3 u_viewPosition;

varying highp vec3 v_vertex;
varying highp vec3 v_normal;

void main()
{
    mediump vec4 finalColor = vec4(0.0);

    /* Ambient Component */
    finalColor += u_ambientColor;

    highp vec3 normal = normalize(v_normal);
    highp vec3 lightDir = normalize(u_lightPosition - v_vertex);

    /* Diffuse Component */
    highp float NdotL = clamp(dot(normal, lightDir), 0.0, 1.0);
    finalColor += (NdotL * u_lightColor * u_diffuseColor);

    /* Specular Component*/
    highp vec3 reflectedLight = reflect(-lightDir, normal);
    highp vec3 viewVector = normalize(u_viewPosition - v_vertex);
    highp float NdotR = clamp(dot(viewVector, reflectedLight), 0.0, 1.0);
    finalColor += pow(NdotR, u_shininess) * u_specularColor;

    finalColor.a = 1.0;
    gl_FragColor = finalColor;
}
