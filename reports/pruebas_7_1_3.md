# Informe de pruebas (sección 7.1.3)

Salidas **crudas** de las pruebas, sin interpretar (única edición: las rutas locales se sustituyeron por `<RAIZ>`, `<TEMP>` y `<usuario>` para no publicar el nombre de usuario del equipo). Las secciones 4 a 7 reproducen la salida literal de cada comando; la tabla de la sección 2 compara esas salidas con los criterios de aceptación de `CLAUDE.md` (sección 8) y los requisitos RNF03 y RNF04.

## 1. Entorno

- Fecha de ejecución: 2026-11-15 02:52
- Último commit al ejecutar: `d2a3a2e Etapa 5: app Streamlit, tema y pruebas de la app`
- Intérprete: Python 3.12.10
- Directorio: raíz del repositorio, con los datasets originales presentes en `datos_locales/` (ningún test de datos se omite)

```
imbalanced-learn==0.14.2
joblib==1.6.0
numpy==2.4.6
pandas==2.2.3
pytest==9.2.0
scikit-learn==1.6.1
streamlit==1.67.0
```

## 2. Verificación de cumplimiento

| Criterio | Esperado | Obtenido | Estado |
|---|---|---|---|
| Pruebas ejecutadas sin fallos ni errores | 0 fallidas, 0 con error | 71 passed | Cumple |
| Pruebas omitidas (un skip no es un «pasó») | 0 | 0 | Cumple |
| Modelo carga sin avisos de versión (scikit-learn 1.6.1 exacto) | sin avisos | ver sección 3 | Cumple |
| Variables recalculadas vs. entrenamiento (78,682 filas) | diferencia máxima ≤ 1e-9, mismos NaN | 3.6e-12 | Cumple |
| Filas con activo_total ≤ 0 en dataset_elaborado | 0 (informe) | 0 | Cumple |
| Integridad (a): puntajes con variables de dataset_prueba | diferencia máxima ≤ 1e-9 | 1.110e-16; 0 observaciones difieren | Cumple |
| Integridad (b): puntajes recalculando desde las cifras | diferencia máxima ≤ 1e-9 | 1.110e-16; 0 observaciones difieren | Cumple |
| Observaciones detectadas (umbral 0.50) | 407 | 407 | Cumple |
| Falsas alarmas (umbral 0.50) | 2,516 | 2516 | Cumple |
| F1 | 0.205 | 0.2049 | Cumple |
| Recall | 0.388 | 0.3880 | Cumple |
| Precisión | 0.139 | 0.1392 | Cumple |
| PR-AUC | 0.135 | 0.1351 | Cumple |
| Cinco primeras importancias | deuda_lp_activos 10.5, tamano_empresa 8.8, valor_mercado_pasivos 7.3, margen_bruto 7.1, margen_neto 6.5 (suman 40.2 %) | deuda_lp_activos 10.5, tamano_empresa 8.8, valor_mercado_pasivos 7.3, margen_bruto 7.1, margen_neto 6.5 (suman 40.2 %) | Cumple |
| Importancia de liquidez_corriente | ≈ 3.7 % | 3.7 % | Cumple |
| RNF03: tiempo de 100 llamadas de puntuar + explicación | máximo < 5 s | mediana 0.0360 s; máximo 0.0754 s | Cumple |
| RNF04: entradas inválidas dan mensajes, no excepciones; mismo dato = mismo puntaje en 100 llamadas | pruebas test_validaciones.py superadas | 36 pasadas, 0 fallidas | Cumple |

## 3. Carga del modelo sin avisos

Comando: `python -W error -c "...cargar_modelo()..."` (cualquier aviso se convierte en excepción). Código de salida: 0.

```
scikit-learn 1.6.1
pasos: ['imputacion', 'winsorizacion', 'escalado', 'smote', 'modelo']
carga con -W error: sin avisos ni excepciones
```

## 4. Pruebas ejecutadas (detalle por archivo)

| Archivo | Qué comprueba | Pasadas | Fallidas | Omitidas |
|---|---|---|---|---|
| `tests/test_app.py` | La app con streamlit.testing: carga, ejemplos, edición de cifras, bloqueos y entrada manual. | 7 | 0 | 0 |
| `tests/test_ejemplos.py` | Casos de ejemplo y plantilla; puntaje recalculado = puntaje_referencia (sin datasets) y verificación contra los datos originales. | 7 | 0 | 0 |
| `tests/test_indicadores.py` | Fórmulas de los 17 indicadores, casos borde (denominador 0, primer año, activo_total ≤ 0, NaN) y comparación contra el entrenamiento por (empresa, año). | 9 | 0 | 0 |
| `tests/test_integridad.py` | Reproducción de puntajes (a y b), conteos 407/2,516, métricas e importancias. | 4 | 0 | 0 |
| `tests/test_limpiar_cuaderno.py` | Script de limpieza de cuadernos con cuadernos sintéticos. | 7 | 0 | 0 |
| `tests/test_rendimiento.py` | RNF03: mediana y máximo de 100 llamadas de puntuar + explicación. | 1 | 0 | 0 |
| `tests/test_validaciones.py` | Bloqueos y avisos con mensajes exactos, lectura de CSV, entradas inválidas sin excepciones (RNF04), determinismo en 100 llamadas y explicación individual. | 36 | 0 | 0 |

Total: 71 passed (suma de la tabla: 71 pasadas). Conteo obtenido del XML de resultados de pytest (`--junitxml`).

## 5. Salida cruda de `pytest -v -rs -s`

Comando: `pytest -v -rs -s -p no:cacheprovider --junitxml=resultados.xml`. Código de salida: 0.

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0 -- <RAIZ>\.venv\Scripts\python.exe
rootdir: <RAIZ>
plugins: anyio-4.16.0
collecting ... collected 71 items

tests/test_app.py::test_carga_sin_excepciones_y_sin_resultado PASSED
tests/test_app.py::test_ejemplos_un_clic[1-Riesgo cr\xedtico-la empresa quebr\xf3] PASSED
tests/test_app.py::test_ejemplos_un_clic[2-Riesgo cr\xedtico-la empresa no quebr\xf3] PASSED
tests/test_app.py::test_ejemplos_un_clic[3-Inversi\xf3n viable-la empresa quebr\xf3] PASSED
tests/test_app.py::test_campos_manuales_parten_del_ejemplo_y_editar_oculta_rotulo PASSED
tests/test_app.py::test_bloqueo_desactiva_el_boton PASSED
tests/test_app.py::test_manual_analizar PASSED
tests/test_ejemplos.py::test_estructura PASSED
tests/test_ejemplos.py::test_puntaje_recalculado_igual_a_referencia PASSED
tests/test_ejemplos.py::test_tipo_coherente_con_umbral_y_riesgo_real PASSED
tests/test_ejemplos.py::test_activo_total_dentro_de_rango_y_sin_bloqueos PASSED
tests/test_ejemplos.py::test_textos_de_interfaz PASSED
tests/test_ejemplos.py::test_plantilla PASSED
tests/test_ejemplos.py::test_casos_coinciden_con_el_conjunto_de_prueba PASSED
tests/test_indicadores.py::test_columnas_y_orden PASSED
tests/test_indicadores.py::test_valores_conocidos PASSED
tests/test_indicadores.py::test_denominador_cero_da_nan_no_infinito PASSED
tests/test_indicadores.py::test_primer_anio_crecimiento_nan PASSED
tests/test_indicadores.py::test_activo_total_no_positivo PASSED
tests/test_indicadores.py::test_nan_de_entrada_da_nan_de_salida PASSED
tests/test_indicadores.py::test_cifra_ausente_y_none_se_tratan_como_nan PASSED
tests/test_indicadores.py::test_varias_filas PASSED
tests/test_indicadores.py::test_contra_entrenamiento 
Filas con activo_total <= 0 en dataset_elaborado: 0

Diferencia máxima por variable: {'liquidez_corriente': 1.1368683772161603e-13, 'prueba_acida': 1.1368683772161603e-13, 'capital_trabajo_activos': 2.2737367544323206e-13, 'endeudamiento': 2.2737367544323206e-13, 'deuda_lp_activos': 7.105427357601002e-15, 'utilidades_retenidas_activos': 1.8189894035458565e-12, 'ebit_activos': 1.1368683772161603e-13, 'roa': 5.684341886080802e-14, 'margen_bruto': 1.8189894035458565e-12, 'margen_ebitda': 1.8189894035458565e-12, 'margen_neto': 1.8189894035458565e-12, 'valor_mercado_pasivos': 3.637978807091713e-12, 'rotacion_activos': 5.684341886080802e-14, 'gastos_operativos_ingresos': 1.8189894035458565e-12, 'rotacion_cuentas_cobrar': 1.8189894035458565e-12, 'crecimiento_ingresos': 4.547473508864641e-13, 'tamano_empresa': 3.552713678800501e-15}
PASSED
tests/test_integridad.py::test_integridad_completa PASSED
tests/test_integridad.py::test_diferencia_maxima_a_y_b PASSED
tests/test_integridad.py::test_conteos_y_criterio PASSED
tests/test_integridad.py::test_importancias PASSED
tests/test_limpiar_cuaderno.py::test_detecta_y_limpia PASSED
tests/test_limpiar_cuaderno.py::test_salida_limpia_y_original_intacto Celdas con executionInfo.user eliminado: 2
Hallazgos antes de limpiar: 4; después: 0
RESULTADO: LIMPIO (sin displayName, userId ni correos)
Escrito: <TEMP>\pytest-of-<usuario>\pytest-12\test_salida_limpia_y_original_0\out.ipynb
PASSED
tests/test_limpiar_cuaderno.py::test_sin_destino_no_escribe Celdas con executionInfo.user eliminado: 2
Hallazgos antes de limpiar: 4; después: 0
RESULTADO: LIMPIO (sin displayName, userId ni correos)
Sin -o ni --in-place: no se escribió ningún archivo.
PASSED
tests/test_limpiar_cuaderno.py::test_in_place Celdas con executionInfo.user eliminado: 2
Hallazgos antes de limpiar: 4; después: 0
RESULTADO: LIMPIO (sin displayName, userId ni correos)
Escrito: <TEMP>\pytest-of-<usuario>\pytest-12\test_in_place0\in.ipynb
PASSED
tests/test_limpiar_cuaderno.py::test_queda_correo_falla_y_no_escribe Celdas con executionInfo.user eliminado: 2
Hallazgos antes de limpiar: 6; después: 2
  QUEDA correo electrónico en $.cells[0].outputs[0].text[0]
  QUEDA correo electrónico en $.cells[1].outputs[0].text[0]
RESULTADO: NO LIMPIO (no se escribió nada)
PASSED
tests/test_limpiar_cuaderno.py::test_queda_clave_en_otro_nivel_falla Celdas con executionInfo.user eliminado: 2
Hallazgos antes de limpiar: 5; después: 1
  QUEDA clave «userId» en $.metadata.colab.provenance[0].userId
RESULTADO: NO LIMPIO (no se escribió nada)
PASSED
tests/test_limpiar_cuaderno.py::test_archivo_invalido_no_lanza No se pudo leer el cuaderno: Expecting value: line 1 column 1 (char 0)
No se pudo leer el cuaderno: [Errno 2] No such file or directory: '<TEMP>\\pytest-of-<usuario>\\pytest-12\\test_archivo_invalido_no_lanza0\\no_existe.ipynb'
PASSED
tests/test_rendimiento.py::test_rendimiento_100_llamadas 
RNF03 (100 llamadas de puntuar + explicacion): mediana 0.0357 s; máximo 0.0392 s; límite 5.0 s
PASSED
tests/test_validaciones.py::test_cifras_completas_sin_bloqueos_ni_avisos PASSED
tests/test_validaciones.py::test_bloqueo_activo_total[None] PASSED
tests/test_validaciones.py::test_bloqueo_activo_total[0] PASSED
tests/test_validaciones.py::test_bloqueo_activo_total[-5] PASSED
tests/test_validaciones.py::test_bloqueo_activo_total[nan] PASSED
tests/test_validaciones.py::test_bloqueo_activo_total[abc] PASSED
tests/test_validaciones.py::test_bloqueo_menos_de_9_cifras PASSED
tests/test_validaciones.py::test_cero_cuenta_como_cifra_presente PASSED
tests/test_validaciones.py::test_aviso_faltan_cifras PASSED
tests/test_validaciones.py::test_avisos_coherencia PASSED
tests/test_validaciones.py::test_avisos_de_escala PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[None] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[entrada1] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[texto] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[5] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[entrada4] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[entrada5] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[entrada6] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[entrada7] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[entrada8] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[entrada9] PASSED
tests/test_validaciones.py::test_entradas_invalidas_no_lanzan[entrada10] PASSED
tests/test_validaciones.py::test_csv_invalido_no_lanza[] PASSED
tests/test_validaciones.py::test_csv_invalido_no_lanza[\xff\xfe\x00] PASSED
tests/test_validaciones.py::test_csv_invalido_no_lanza[a,b\n] PASSED
tests/test_validaciones.py::test_csv_invalido_no_lanza[\x00\x01\x02] PASSED
tests/test_validaciones.py::test_csv_invalido_no_lanza[\xf1;\xf1\n1;2] PASSED
tests/test_validaciones.py::test_csv_invalido_no_lanza[activo_total\nabc] PASSED
tests/test_validaciones.py::test_csv_invalido_no_lanza[None] PASSED
tests/test_validaciones.py::test_csv_invalido_no_lanza[12345] PASSED
tests/test_validaciones.py::test_csv_coma_y_primera_fila PASSED
tests/test_validaciones.py::test_csv_punto_y_coma_con_coma_decimal PASSED
tests/test_validaciones.py::test_csv_valor_no_numerico_y_columnas_faltantes PASSED
tests/test_validaciones.py::test_mismo_dato_mismo_puntaje_100_llamadas PASSED
tests/test_validaciones.py::test_explicacion_un_solo_predict_proba PASSED
tests/test_validaciones.py::test_explicacion_variable_sin_dato_efecto_cero PASSED

- generated xml file: <TEMP>\claude\fe71f2a53ef08c9a\a9e23ee9-3f55-44db-8cf7-f5024564d73d\scratchpad\resultados.xml -
============================= 71 passed in 16.33s =============================
2026-11-15 02:51:45.627 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 02:51:46.197 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 02:51:47.301 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 02:51:47.592 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 02:51:47.830 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 02:51:48.147 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 02:51:48.412 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
```

## 6. Salida cruda de `scripts/verificar_integridad.py`

Código de salida: 0 (0 = coincide).

```
=== Prueba de integridad ===
Observaciones: 15742 | empresas: 1794
(a) variables de dataset_prueba.csv: diferencia máxima 1.110e-16; observaciones que difieren (> 1e-09): 0
(b) variables recalculadas con indicadores.py: diferencia máxima 1.110e-16; observaciones que difieren (> 1e-09): 0
(b) cruce por (empresa, anio): 15742 filas; primeros años: 1794; ingresos_anio_anterior NaN: 1794
Observaciones de riesgo: 1049
  criterio '>=': detectadas=407 falsas_alarmas=2516 F1=0.2049 recall=0.3880 precisión=0.1392
  criterio '>': detectadas=407 falsas_alarmas=2516 F1=0.2049 recall=0.3880 precisión=0.1392
Criterio usado por el repositorio: '>='; clasificar() sobre (b): detectadas=407, falsas_alarmas=2516
PR-AUC: 0.1351 (referencia sin capacidad predictiva: 0.0666)
Importancias (17 variables, %):
deuda_lp_activos                10.5
tamano_empresa                   8.8
valor_mercado_pasivos            7.3
margen_bruto                     7.1
margen_neto                      6.5
utilidades_retenidas_activos     5.8
endeudamiento                    5.6
rotacion_activos                 5.5
rotacion_cuentas_cobrar          5.3
gastos_operativos_ingresos       5.2
margen_ebitda                    5.1
capital_trabajo_activos          5.0
prueba_acida                     4.9
crecimiento_ingresos             4.8
roa                              4.6
ebit_activos                     4.2
liquidez_corriente               3.7
RESULTADO: COINCIDE
```

## 7. Salida cruda de `tests/test_rendimiento.py` (RNF03)

Comando: `pytest tests/test_rendimiento.py -v -rs -s`. Código de salida: 0.

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0 -- <RAIZ>\.venv\Scripts\python.exe
rootdir: <RAIZ>
plugins: anyio-4.16.0
collecting ... collected 1 item

tests/test_rendimiento.py::test_rendimiento_100_llamadas 
RNF03 (100 llamadas de puntuar + explicacion): mediana 0.0360 s; máximo 0.0754 s; límite 5.0 s
PASSED

============================== 1 passed in 6.31s ==============================
```
