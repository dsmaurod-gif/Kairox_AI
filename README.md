# Kairox AI

Sistema predictivo de viabilidad de inversión. A partir de 16 cifras financieras de una empresa (en millones de dólares), calcula 17 indicadores y un modelo Random Forest ya entrenado la clasifica como **inversión viable** (0) o **riesgo crítico** (1).

Proyecto universitario de la Universidad Privada Antenor Orrego (UPAO), curso *Inteligencia Artificial: Principios y Técnicas*, ciclo 2026-20.

## Para qué sirve y para qué no

Responde una sola pregunta: si la empresa es un destino viable para el capital o presenta riesgo crítico. Requiere cifras de al menos un ejercicio contable completo, en millones de dólares, y supone que la información es veraz (no detecta manipulación contable). No define el monto, el momento de entrada ni el tipo de instrumento, y no reemplaza el análisis financiero ni el criterio de quien decide.

## Cómo interpretar el puntaje

El resultado es un **puntaje de riesgo entre 0 y 1** con umbral de decisión 0.50. **No es una probabilidad**: el modelo se entrenó con clases equilibradas mediante SMOTE y su salida no está calibrada. Una clasificación de riesgo crítico es una alerta para revisar la empresa, no una conclusión.

## Desempeño real

Evaluado una sola vez sobre empresas que el modelo no vio al entrenar (15,742 observaciones de 1,794 empresas), con umbral 0.50:

| Métrica | Valor |
|---|---|
| F1 | 0.205 (IC 95 %: 0.170–0.238) |
| Recall | 0.388 (IC 95 %: 0.334–0.443) |
| Precisión | 0.139 |
| PR-AUC | 0.135 (referencia sin capacidad predictiva: 0.067) |
| Detectadas / falsas alarmas | 407 de 1,049 observaciones de riesgo / 2,516 |

La meta de F1 0.80 fue una aspiración **no alcanzada**. En la prueba, el modelo detectó 4 de cada 10 observaciones de riesgo y solo una de cada siete alertas fue real.

## Cómo ejecutarlo

Requiere Python 3.12 (scikit-learn 1.6.1 no publica ruedas para Python 3.14, y el archivo del modelo exige exactamente esa versión).

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app/app.py
```

La app ofrece tres métodos de entrada: **empresa de ejemplo** (tres casos reales del conjunto de prueba), **subir archivo** (CSV con las 16 cifras; hay una plantilla descargable) e **ingresar manualmente**.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q -rs
```

`-rs` lista las pruebas omitidas. Las pruebas que requieren los datasets originales (carpeta `datos_locales/`, no incluida en el repositorio) se omiten con un mensaje explícito si faltan; **una prueba omitida no cuenta como superada**. La prueba de integridad (`scripts/verificar_integridad.py`) demuestra que el código del repositorio reproduce los puntajes de la evaluación original con una diferencia máxima inferior a 1e-9. Las salidas completas están en [reports/pruebas_7_1_3.md](reports/pruebas_7_1_3.md).

## Estructura

```
app/app.py                  Aplicación web (Streamlit)
src/kairox/                 transformadores, indicadores, modelo, validaciones, explicacion, ejemplos
models/                     Modelo entrenado (fijo), metadatos y parámetros
data/                       Casos de ejemplo, plantilla de empresa y nota sobre los datos
scripts/                    Selección de ejemplos, prueba de integridad, limpieza de cuadernos
notebooks/                  Cuaderno de entrenamiento y evaluación (sin metadatos de cuenta)
tests/                      Pruebas automáticas
docs/                       Arquitectura, guía de estilo, declaración de uso de IA y registro de avance
reports/                    Importancias del modelo y salidas crudas de las pruebas
.streamlit/config.toml      Tema de la app
```

Más detalle en [docs/arquitectura.md](docs/arquitectura.md).

## Datos

El conjunto de datos completo no se incluye. Ver [data/README_datos.md](data/README_datos.md).

## Limitaciones

- El desempeño es bajo (F1 0.205): la mayoría de las alertas son falsas alarmas y más de 6 de cada 10 observaciones de riesgo no se detectan.
- El puntaje no está calibrado y no debe leerse como probabilidad de quiebra.
- Se entrenó con datos de empresas estadounidenses entre 1999 y 2018; no hay garantía fuera de ese contexto.
- Las cifras ingresadas se suponen veraces y completas. Si faltan datos, se imputan con la mediana de entrenamiento y el resultado es menos confiable.
- La explicación individual es una aproximación: compara cada variable con la empresa típica, una a la vez, sin probar causalidad ni recoger interacciones.

## Declaración de uso de inteligencia artificial

Se utilizaron **Claude (Claude Code)** y **Gemini**. El detalle está en [docs/declaracion_uso_ia.md](docs/declaracion_uso_ia.md).

## Equipo

- Glidis Aguirre
- Diego Mauricio

## Licencia

MIT. Ver el archivo [LICENSE](LICENSE).
