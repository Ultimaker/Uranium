uniform vec4 u_ambientColor;
uniform vec4 u_diffuseColor;
uniform vec4 u_specularColor;

uniform vec3 u_lightPosition;
uniform float u_lightIntensity;
uniform vec4 u_lightColor;

uniform vec3 u_viewPosition;

uniform float u_ambientFactor;
uniform float u_diffuseFactor;
uniform float u_specularFactor;
uniform float u_specularStrength;

varying vec3 v_vertex;
varying vec3 v_normal;

void main()
{
    vec4 finalColor = vec4(0.0, 0.0, 0.0, 0.0);

    /* Ambient Component */
    finalColor += u_ambientFactor * u_ambientColor;

    /* Diffuse Component */
    vec3 lightDir = normalize(u_lightPosition - v_vertex);

    float NdotL = dot(v_normal, lightDir);
    float intensity = clamp(NdotL, 0.0, 1.0);

    finalColor += u_diffuseFactor * (intensity * u_lightColor * u_diffuseColor) * u_lightIntensity;

    /* Specular Component*/
    vec3 viewDir = normalize(u_viewPosition - v_vertex);
    vec3 halfVector = normalize(lightDir + viewDir);

    float NdotH = dot(v_normal, halfVector);
    intensity = pow(clamp(NdotH, 0.0, 1.0), u_specularStrength);

    finalColor += u_specularFactor * (intensity * u_specularColor);

    finalColor.a = 1.0;
    gl_FragColor = finalColor;
}
