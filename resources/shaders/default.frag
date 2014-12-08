uniform vec4 u_ambientColor;
uniform vec4 u_diffuseColor;
uniform vec4 u_specularColor;

uniform vec3 u_lightPosition;
uniform vec4 u_lightColor;

uniform float u_shininess;

uniform vec3 u_viewPosition;

varying vec3 v_vertex;
varying vec3 v_normal;

void main()
{
    vec4 finalColor = vec4(0.0);

    /* Ambient Component */
    finalColor += u_ambientColor;

    vec3 normal = normalize(v_normal);
    vec3 lightDir = normalize(u_lightPosition - v_vertex);

    /* Diffuse Component */
    float NdotL = clamp(dot(normal, lightDir), 0.0, 1.0);
    finalColor += (NdotL * u_lightColor * u_diffuseColor);

    /* Specular Component*/
    vec3 reflectedLight = reflect(-lightDir, normal);
    vec3 viewVector = normalize(u_viewPosition - v_vertex);
    float NdotR = clamp(dot(viewVector, reflectedLight), 0.0, 1.0);
    finalColor += pow(NdotR, u_shininess) * u_specularColor;

    finalColor.a = 1.0;
    gl_FragColor = finalColor;
}
