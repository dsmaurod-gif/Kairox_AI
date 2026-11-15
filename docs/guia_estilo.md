# Guía de estilo — Kairox AI

La app reproduce el flujo y el aspecto del prototipo de diseño, sin necesidad de coincidir al píxel. El producto se llama **Kairox AI** (el prototipo decía «Investia AI»). Todo el texto de la interfaz va en español, en tono académico y formal.

## Tipografía

- **Decisión del proyecto:** se usan las tipografías del sistema (`sans-serif` para texto y títulos, `monospace` para cifras) para evitar peticiones externas y asegurar una carga inmediata.
- La especificación original prevé Plus Jakarta Sans (400–800) y JetBrains Mono para las cifras; no se cargan en esta versión.

## Colores

| Uso | Valor |
|---|---|
| Primario | `#5B3DB5` (hover `#47299A`) |
| Acento (solo títulos grandes y gráficos) | `#8A64DB` |
| Fondos | `#EDE6FB`, `#F1ECFB`, `#F8F5FE` |
| Bordes | `#E9E1F8`, `#CDBEF0` |
| Texto | `#1B1340` (secundarios `#4A4568`, `#5A5578`, `#6B6688`) |
| Riesgo | fondo `#FBE3E8`, texto `#8E1F3A`, barra `#A12A47` |
| Viable | fondo `#DDF3E1`, texto `#17612F` |
| Avisos | fondo `#FFF6DC`, borde `#F1DFA3`, texto `#5C4707` |

## Forma y accesibilidad

- Tarjetas con radio de 18 a 24 px; botones con radio de 12 a 14 px.
- Controles de al menos 44 px de alto.
- Foco visible de 3 px en `#8A64DB`.
- Diseño legible en celular: en pantallas estrechas el contenido pasa a una columna. La tercera pestaña de entrada («Ingresar manualmente») puede desplazarse horizontalmente en pantallas muy pequeñas; se aceptó para conservar la etiqueta de la especificación.
- Botón desactivado con contraste suficiente (fondo `#CDBEF0`, texto `#4A4568`).

## Contenido y lenguaje

- El puntaje se muestra en escala 0–1 con dos decimales y umbral 0.50. **Nunca** se presenta como porcentaje ni se llama «probabilidad».
- No se prometen exactitud ni frases del tipo «decisiones más seguras».
- Las únicas cifras de desempeño permitidas en la interfaz son las medidas en la prueba: F1 0.205 (IC 95 %: 0.170–0.238), recall 0.388 (0.334–0.443), precisión 0.139, PR-AUC 0.135 (referencia sin capacidad predictiva: 0.067) y umbral 0.50. La meta de F1 0.80 es una aspiración no alcanzada.
- La configuración del tema está en `.streamlit/config.toml`; el CSS adicional, en `app/app.py`.
