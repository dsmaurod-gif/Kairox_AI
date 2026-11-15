# Declaración de uso de inteligencia artificial

## Herramientas utilizadas

- **Claude (Claude Code)**, de Anthropic. En este repositorio se usó el modelo Claude Sonnet 5.5, ejecutado desde la extensión de VS Code.
- **Gemini**, de Google. Se utilizó para:
  - asistencia en la configuración del entorno Git y VS Code;
  - evaluación técnica de decisiones de arquitectura y del determinismo del modelo (fijación de `n_jobs=1`);
  - validación de criterios de diseño de la interfaz;
  - revisión de decisiones por etapa.

## Uso de Claude Code en este repositorio

Claude Code se usó para construir el repositorio de despliegue, siguiendo el documento de especificación `CLAUDE.md`, por etapas:

1. entorno y dependencias fijadas;
2. estructura, `transformadores.py` e `indicadores.py` con sus pruebas;
3. `modelo.py` y la prueba de integridad;
4. `validaciones.py`, `explicacion.py` y las pruebas de rendimiento y de entradas inválidas;
5. casos de ejemplo y plantilla;
6. la aplicación Streamlit y su tema;
7. documentación, script de limpieza de cuadernos e informe de pruebas.

## Decisiones y verificación humanas

- Las personas del equipo fijaron las reglas del proyecto: no reentrenar el modelo, no cambiar el umbral ni las fórmulas, no inventar cifras y no mostrar el puntaje como probabilidad.
- Cada etapa se presentó como un plan, fue aprobada por el equipo antes de implementarse y se revisó al cerrarla. El `git push` lo realizó el equipo a mano.
- El equipo aprobó las decisiones que la especificación dejaba abiertas: la regla de selección de los casos de ejemplo, el criterio de clasificación, la fijación de `n_jobs=1` al cargar el modelo, el uso de tipografías del sistema y la licencia.
- Cuando una prueba falló o apareció un hallazgo inesperado (por ejemplo, la variación de último bit del puntaje), se detuvo el trabajo, se reportó y el equipo decidió.
- Los resultados se verificaron con pruebas automáticas ejecutadas durante el desarrollo y registradas en `docs/avance.md` y `reports/pruebas_7_1_3.md`.

## Alcance y límites

- Claude Code no reentrenó ni modificó el modelo: el archivo `modelo_final.joblib` es el entregado por el equipo.
- El conjunto de prueba solo se leyó para la prueba de integridad y para elegir los 3 casos de ejemplo; nunca para decidir nada sobre el modelo.
- No se subieron al repositorio los datasets completos, credenciales ni metadatos de cuenta de los cuadernos.
- El equipo es responsable del contenido final del repositorio.
