# Registro de avance — Kairox AI

## Etapa 0 — Entorno (2026-11-15)

**Estado inicial:** rama `main` sin commits; remoto `origin` = https://github.com/dsmaurod-gif/Kairox_AI.git, vacío (`git fetch origin` no devolvió ramas). Solo existía `.gitignore` sin seguimiento.

**Decisiones**
- **Python 3.12.10 (no 3.14.4).** El equipo solo tenía Python 3.14.4, para el cual `scikit-learn==1.6.1` no publica ruedas (`pip download` → «No matching distribution found»). Como el `.joblib` exige exactamente scikit-learn 1.6.1, se instaló Python 3.12 y se creó `.venv` con `py -3.12 -m venv .venv`. (Colab usó Python 3.13.18 según `versiones_entorno.json`; no coincide exactamente, pero el modelo carga sin avisos.)
- **numpy 2.4.6** (versión de Colab) se instaló sin problemas; no se relajó ninguna versión.
- **streamlit 1.67.0** y **pytest 9.2.0**: versiones estables instaladas, fijadas en `requirements*.txt`.
- `.gitignore` reescrito sin BOM UTF-8 (la primera línea lo tenía). Contenido sin cambios.
- `CLAUDE.md` permanece en `datos_locales/` (ignorada); no se copia a la raíz hasta que se indique.

**Salidas crudas**
```
Python 3.12.10 (.venv)
scikit-learn==1.6.1  imbalanced-learn==0.14.2  joblib==1.6.0
pandas==2.2.3  numpy==2.4.6  streamlit==1.67.0  pytest==9.2.0

Carga de modelo_final.joblib (warnings.simplefilter("always")):
sklearn 1.6.1
pasos: ['imputacion', 'winsorizacion', 'escalado', 'smote', 'modelo']
avisos: 0
```

## Etapa 1 — Estructura, transformadores e indicadores (2026-11-15)

**Hecho**
- Carpetas del repositorio (sección 5; las vacías llevan `.gitkeep`), `CLAUDE.md` copiado a la raíz y los 3 JSON en `models/` (verificado: `models/` no está ignorado por git). El `.joblib` entra en la etapa 2.
- `src/kairox/transformadores.py`: `Winsorizador` copiado tal cual (sección 6.1).
- `src/kairox/indicadores.py`: `calcular_variables()`; el orden de las 17 columnas se lee de `models/modelo_final_metadatos.json`. También expone `CIFRAS_ENTRADA`, `ETIQUETAS_CIFRAS` e `INDICADORES` (etiqueta, fórmula, descripción) para la app y el glosario.
- `tests/test_indicadores.py` + `tests/conftest.py`. Las rutas se calculan desde la raíz del repositorio (`Path(__file__).resolve().parents[1]`), de modo que pytest funciona desde cualquier carpeta; si faltan los datasets la prueba se omite con el mensaje «requiere datos_locales/…».

**Decisión:** solo el denominador 0 produce NaN (sección 6.3). Con `activo_total` < 0 los ratios se calculan con su signo y `tamano_empresa` = 0; el bloqueo de `activo_total` ≤ 0 corresponde a `validaciones.py` (etapa 3).

**Criterio de aceptación:** en la máquina de desarrollo no debe omitirse ninguna prueba (un skip no es un «pasó»). Se ejecuta `pytest -q -rs` al cierre de cada etapa.

**Salida cruda** (`pytest -q -rs -s`, ejecutado desde `tests/`)
```
9 passed in 1.38s   (sin pruebas omitidas)
Diferencia máxima por variable (recalculado vs dataset_filtrado, 78,682 filas, mismos NaN):
liquidez_corriente 1.1e-13 | prueba_acida 1.1e-13 | capital_trabajo_activos 2.3e-13
endeudamiento 2.3e-13 | deuda_lp_activos 7.1e-15 | utilidades_retenidas_activos 1.8e-12
ebit_activos 1.1e-13 | roa 5.7e-14 | margen_bruto 1.8e-12 | margen_ebitda 1.8e-12
margen_neto 1.8e-12 | valor_mercado_pasivos 3.6e-12 | rotacion_activos 5.7e-14
gastos_operativos_ingresos 1.8e-12 | rotacion_cuentas_cobrar 1.8e-12
crecimiento_ingresos 4.5e-13 | tamano_empresa 3.6e-15
```

### Etapa 1 — ajustes tras la revisión
- Criterio aprobado: los ratios usan división simple (solo denominador 0 → NaN); el bloqueo de `activo_total` ≤ 0 vive en `validaciones.py`.
- `dataset_elaborado.csv`: **0 filas** con `activo_total` ≤ 0 (0 iguales a cero, 0 negativas, 0 NaN), por lo que no hay casos que contrastar con `dataset_filtrado.csv`; la prueba falla si aparece alguno.
- La comparación se alinea por (`empresa`, `anio`) con `merge` externo y `validate="one_to_one"`; la prueba falla si alguna clave no está en ambos conjuntos. `tamano_empresa` se compara contra `dataset_filtrado.csv` con el mismo mecanismo.
- Salida: `9 passed`, sin omitidas; «Filas con activo_total <= 0 en dataset_elaborado: 0».

## Etapa 2 — Modelo y prueba de integridad (2026-11-15)

**Hecho**
- `models/modelo_final.joblib` copiado (24,083,977 bytes = 24.08 MB; `models/` no está en `.gitignore`).
- `src/kairox/modelo.py`: `cargar_modelo()` (expone `Winsorizador` en `__main__` antes de `joblib.load`), `puntuar()` (exige las 17 columnas en el orden de los metadatos y falla ante avisos de nombres de columnas), `clasificar()` (criterio `>=`, constante `CRITERIO`) e `importancias()`.
- `scripts/verificar_integridad.py` y `tests/test_integridad.py` (rutas desde la raíz; `skip` explícito si faltan los datos). Guarda `reports/importancias_modelo.csv` (17 variables).

**Verificaciones (a) y (b), ambas obligatorias**
- (a) variables ya calculadas en `dataset_prueba.csv`; (b) variables recalculadas con `indicadores.py` desde las cifras, cruzando por (`empresa`, `anio`) con `dataset_elaborado.csv` (15,742 filas) y `ingresos_anio_anterior` = `shift(1)` por empresa.
- El primer año de cada empresa deja `ingresos_anio_anterior` en NaN: 1,794 primeros años = 1,794 NaN.

**Observación:** los criterios `>=` y `>` dan los mismos conteos (ningún puntaje de la prueba es exactamente 0.50), por lo que la prueba no distingue entre ambos. Se mantiene `>=` según la sección 6.2.

**Salida cruda** (`python scripts/verificar_integridad.py`, exit=0)
```
Observaciones: 15742 | empresas: 1794
(a) diferencia máxima 3.331e-16; observaciones que difieren (> 1e-09): 0
(b) diferencia máxima 4.441e-16; observaciones que difieren (> 1e-09): 0
(b) cruce por (empresa, anio): 15742 filas; primeros años: 1794; ingresos_anio_anterior NaN: 1794
Observaciones de riesgo: 1049
  criterio '>=': detectadas=407 falsas_alarmas=2516 F1=0.2049 recall=0.3880 precisión=0.1392
  criterio '>':  detectadas=407 falsas_alarmas=2516 F1=0.2049 recall=0.3880 precisión=0.1392
clasificar() sobre (b): detectadas=407, falsas_alarmas=2516
PR-AUC: 0.1351 (referencia sin capacidad predictiva: 0.0666)
Importancias (%): deuda_lp_activos 10.5 | tamano_empresa 8.8 | valor_mercado_pasivos 7.3 |
margen_bruto 7.1 | margen_neto 6.5 | utilidades_retenidas_activos 5.8 | endeudamiento 5.6 |
rotacion_activos 5.5 | rotacion_cuentas_cobrar 5.3 | gastos_operativos_ingresos 5.2 |
margen_ebitda 5.1 | capital_trabajo_activos 5.0 | prueba_acida 4.9 | crecimiento_ingresos 4.8 |
roa 4.6 | ebit_activos 4.2 | liquidez_corriente 3.7
RESULTADO: COINCIDE
pytest -q -rs: 13 passed in 6.83s (sin omitidas)
```

## Etapa 3 — Validaciones, explicación y rendimiento (2026-11-15)

**Hecho**
- `src/kairox/validaciones.py`: `validar_cifras()` (bloqueos, avisos y escala con los límites de `parametros_modelo.json`) y `leer_csv()` (devuelve `(cifras, mensajes)`; separador `,` o `;`, coma decimal con `;`, solo la primera fila, nunca lanza excepciones). Un 0 cuenta como cifra presente; las columnas ausentes del CSV se tratan como cifras faltantes (avisos y bloqueos normales). El rango [p1, p99] de `activo_total` solo avisa: el recorte lo hace el modelo.
- `src/kairox/explicacion.py`: `explicar()` puntúa la fila original y las 17 variantes (variable → mediana de entrenamiento) en **un solo** `predict_proba`; muestra las 5 de mayor |efecto| con signo, valor y «sin dato» (efecto 0), más el texto obligatorio de aproximación.
- `tests/test_validaciones.py` (RNF04 y explicación) y `tests/test_rendimiento.py` (RNF03).

**Hallazgo (RNF04):** el mismo dato daba 3 puntajes distintos en 100 llamadas (diferencias de 1 ulp, ~3e-17). Causa: el bosque se guardó con `n_jobs=-1` y la suma de árboles en hilos cambia de orden. Decisión aprobada: `cargar_modelo()` fija `n_jobs=1` **en memoria** (el `.joblib` no cambia; no es un hiperparámetro que afecte lo que el modelo predice). Con ello las 100 llamadas dan exactamente el mismo valor. Se descartaron redondear el puntaje y relajar la prueba con tolerancia.

**Salida cruda** (3 ejecuciones consecutivas de `pytest -q -rs -s`)
```
50 passed in 13.90s / 13.65s / 13.26s   — sin omitidas
RNF03 (100 llamadas de puntuar + explicacion): mediana 0.0387 s; máximo 0.0622 s; límite 5.0 s
RNF03 (otras 2 ejecuciones): mediana 0.0377 s, máx 0.0471 s | mediana 0.0371 s, máx 0.0479 s
(antes del cambio, con n_jobs=-1: mediana 0.1211 s; máximo 0.3497 s)
Integridad tras el cambio: (a) y (b) diferencia máxima 1.110e-16, 0 observaciones difieren;
407 detectadas, 2516 falsas alarmas; RESULTADO: COINCIDE
```

## Etapa 4 — Ejemplos y plantilla (2026-11-15)

**Hecho**
- `scripts/seleccionar_ejemplos.py`, `data/ejemplos_prueba.csv` (3 casos reales del conjunto de prueba), `data/plantilla_empresa.csv` (16 columnas y una fila con cifras ficticias), `src/kairox/ejemplos.py` (carga, rótulos y «Lo que ocurrió») y `tests/test_ejemplos.py`.
- **Regla de selección (6.6, confirmada por el responsable):** la mediana del puntaje se calcula sobre **todas** las observaciones de la categoría (par: promedio de los dos centrales); el representante es, entre las observaciones con año anterior disponible y `activo_total` dentro de [p1, p99], la de puntaje más cercano a esa mediana; desempate por (`empresa`, `anio`). `anio` es entero y el CSV solo lleva las columnas pedidas.
- El conjunto de prueba se usó solo para leer y elegir los 3 casos.

**Hallazgo menor:** `pd.read_csv` con el lector rápido altera el último bit de un decimal (0.31580793276042757 → 0.3158079327604275). `cargar_ejemplos()` usa `float_precision="round_trip"` y la prueba contra `proba_prueba.npy` compara con `==`.

**Salida cruda**
```
acierto: 407 observaciones, 386 elegibles, mediana 0.640806 -> C_333 2009 (puntaje 0.640806)
falsa alarma: 2516 observaciones, 2328 elegibles, mediana 0.602984 -> C_2595 2015 (puntaje 0.603001)
caso no detectado: 642 observaciones, 536 elegibles, mediana 0.315374 -> C_5658 2008 (puntaje 0.315808)
pytest -q -rs (repositorio, con datos_locales/): 57 passed, sin omitidas
pytest tests/test_ejemplos.py (copia SIN datos_locales/): 6 passed, 1 skipped
  SKIPPED: requiere datos_locales/dataset_prueba.csv   (la prueba contra los datos originales)
```

## Etapa 5 — App Streamlit (2026-11-15)

**Hecho**
- `.streamlit/config.toml` (tema de la sección 10; sin estadísticas de uso), `app/app.py` y `tests/test_app.py` (`streamlit.testing.v1.AppTest`, 7 pruebas).
- App en una sola página, 2 pasos: **1 Datos** (tres métodos en pestañas: empresa de ejemplo, subir archivo con plantilla descargable, ingresar manualmente) y **2 Resultado** (anillo con el puntaje `0.xx`, etiqueta, barra con «Umbral 0.50», explicación individual, variables que más usa el modelo, «Cómo leer este resultado», tiempo de cálculo). Glosario de 17 indicadores y sección «Modelo» con las métricas permitidas.
- Decisiones aprobadas: tipografías del sistema (`sans-serif`/`monospace`, sin peticiones externas); el resultado aparece debajo del formulario sin ocultarlo y **se recalcula** al modificar cifras; los campos manuales parten de las cifras del ejemplo o del archivo; el rótulo del caso y «Lo que ocurrió» se ocultan en cuanto se edita un valor; `guia_estilo.md` queda para la etapa 6.
- Un clic en un ejemplo carga las 16 cifras y analiza de inmediato; «Analizar empresa» queda desactivado mientras haya bloqueos.
- Nunca se muestra el puntaje como probabilidad ni porcentaje (escala 0–1, dos decimales).

**Verificación en navegador** (servidor `streamlit run app/app.py` + Edge sin interfaz controlado por CDP; guion auxiliar fuera del repositorio)
- Ancho 1000 px y 390 px (celular): sin desborde horizontal (`scrollWidth` = `clientWidth`); en celular todo pasa a una columna.
- Probados los 3 métodos: ejemplos (acierto, falsa alarma, caso no detectado), archivo (plantilla → puntaje 0.18, «Inversión viable»; origen «Archivo (plantilla_empresa.csv)») y campos manuales tras cargar un ejemplo.
- Corregido tras la inspección visual: el botón «Analizar empresa» desactivado tenía contraste ilegible.
- **Observación pendiente (cosmética):** en pantalla de 390 px la tercera pestaña («Ingresar manualmente») queda parcialmente recortada y se desplaza con el indicador «›».
- Limitación: la verificación visual fue con Edge en modo sin interfaz; no se probó en un celular real ni con otros navegadores.

**Salida cruda**
```
servidor: Uvicorn started on :::8599; GET / -> 200; /_stcore/health -> ok
pytest -q -rs: 64 passed in 22.60s   (sin omitidas)
tests/test_app.py: 7 passed
Tiempo de cálculo mostrado en pantalla: 0.043 s (ejemplo), 0.137 s (primera carga del archivo)
```
