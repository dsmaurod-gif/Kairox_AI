# Arquitectura

## Visión general

El sistema usa **un único modelo fijo** (`models/modelo_final.joblib`), el mismo que se evaluó en el conjunto de prueba. El repositorio no reentrena ni ajusta nada: solo lo carga, lo puntúa y lo explica.

```
16 cifras de entrada ──► validaciones ──► indicadores ──► 17 variables ──► modelo ──► puntaje (0–1)
 (CSV, ejemplo o manual)   bloqueos/avisos   calcular_variables            pipeline        │
                                                                                          ├─► clasificación (umbral 0.50)
                                                                                          └─► explicación individual
```

El pipeline guardado (imblearn) tiene los pasos `imputacion` → `winsorizacion` → `escalado` → `smote` → `modelo`. SMOTE solo actúa al entrenar; al puntuar se aplican imputación (mediana), recorte a los percentiles 1 % y 99 %, escalado y el Random Forest.

## Módulos (`src/kairox/`)

| Módulo | Responsabilidad |
|---|---|
| `transformadores.py` | Clase `Winsorizador`, copiada tal cual: el modelo guardado la necesita para cargarse. |
| `indicadores.py` | `calcular_variables()`: de las 16 cifras a las 17 variables. Denominador 0 → NaN (nunca infinito); NaN en la entrada → NaN en la salida. Expone etiquetas y fórmulas para la app y el glosario. El orden de las columnas se lee de los metadatos del modelo. |
| `modelo.py` | `cargar_modelo()`, `puntuar()`, `clasificar()` e `importancias()`. |
| `validaciones.py` | `validar_cifras()` (bloqueos y avisos) y `leer_csv()`. Entradas inválidas producen mensajes, no excepciones. |
| `explicacion.py` | Sensibilidad individual: cada variable se sustituye por su mediana de entrenamiento y se mide el cambio del puntaje; las 17 variantes se calculan en un solo `predict_proba`. |
| `ejemplos.py` | Carga los 3 casos reales de ejemplo, sus rótulos y la plantilla. |

`app/app.py` es la interfaz Streamlit (una sola página, flujo de 2 pasos); agrega `src/` a `sys.path` y no requiere instalar el paquete.

## Decisiones técnicas relevantes

- **`Winsorizador` en `__main__`.** El archivo `.joblib` se guardó con la clase definida en `__main__` (cuaderno de Colab). Antes de `joblib.load`, `cargar_modelo()` la expone en `sys.modules['__main__']`.
- **`n_jobs=1` en memoria.** El bosque se guardó con `n_jobs=-1`; sumar los 300 árboles en varios hilos cambia el orden de suma y el puntaje variaba en el último bit (~3e-17) entre llamadas. `cargar_modelo()` fija `n_jobs=1` en memoria para que el mismo dato dé exactamente el mismo puntaje. No es un hiperparámetro que cambie lo que el modelo predice, y el archivo no se modifica.
- **Criterio `>=`.** Un caso es de riesgo crítico si `puntaje >= umbral` (0.50). En el conjunto de prueba ningún puntaje vale exactamente 0.50, por lo que `>=` y `>` dan los mismos conteos; se mantuvo `>=`.
- **Versiones fijas.** scikit-learn debe ser exactamente 1.6.1 (el `.joblib` es sensible a la versión). Con Python 3.14 no existen ruedas de esa versión; se usa Python 3.12.
- **Puntaje no calibrado.** SMOTE equilibró las clases al entrenar; el puntaje es un indicador de riesgo relativo, no una probabilidad.
- **Una sola cifra de ingresos.** En el entrenamiento `ventas_netas` e `ingresos_totales` son idénticas, por lo que la app pide solo `ingresos_totales`.

## Cómo se comprueba que la app usa el modelo evaluado

`scripts/verificar_integridad.py` aplica el código del repositorio a las 15,742 observaciones del conjunto de prueba, de dos maneras: (a) con las 17 variables ya calculadas y (b) recalculándolas desde las cifras con `indicadores.py` (cruzando por empresa y año, con el ingreso del año anterior derivado del dataset). Compara con los puntajes de referencia (diferencia máxima ≤ 1e-9), reproduce los conteos (407 detectadas, 2,516 falsas alarmas) y las métricas, y comprueba las importancias globales. `tests/test_integridad.py` lo ejecuta dentro de `pytest`.

## Pruebas

| Archivo | Qué verifica |
|---|---|
| `test_indicadores.py` | Fórmulas, casos borde y coincidencia con el entrenamiento (≤ 1e-9, mismos NaN). |
| `test_integridad.py` | Reproducción de puntajes, conteos, métricas e importancias. |
| `test_validaciones.py` | Bloqueos y avisos, lectura de CSV, entradas inválidas sin excepciones (RNF04), determinismo en 100 llamadas y explicación individual. |
| `test_rendimiento.py` | Tiempo de 100 llamadas de `puntuar` + `explicacion` (RNF03). |
| `test_ejemplos.py` | Los 3 casos: el puntaje recalculado debe igualar `puntaje_referencia`; corre sin los datasets. |
| `test_app.py` | La app con `streamlit.testing`: carga, ejemplos, edición de cifras y bloqueos. |
| `test_limpiar_cuaderno.py` | El script de limpieza de cuadernos, con cuadernos sintéticos. |
