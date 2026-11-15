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
