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
