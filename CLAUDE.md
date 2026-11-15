# CLAUDE.md — Kairox AI: despliegue del sistema predictivo de viabilidad de inversión

## 0. Alcance actual
**Bloque 1 = etapas 0 a 3 de la sección 9.** No empieces la etapa 4 ni las siguientes hasta que yo lo indique por escrito. Al terminar la etapa 3, muestra `git log --oneline` y `git ls-files`, y detente.

## 1. Contexto
Proyecto universitario (UPAO, curso Inteligencia Artificial: Principios y Técnicas, 2026-20). Un Random Forest **ya entrenado** (no se reentrena aquí) clasifica una empresa como 0 = inversión viable o 1 = riesgo crítico a partir de 17 variables (16 ratios financieros + `tamano_empresa`). Dataset de origen: American Companies Bankruptcy Prediction Dataset (Kaggle; Lombardo et al., 2022): 78,682 observaciones anuales de 8,971 empresas (1999–2018).

El producto se llama **Kairox AI** (el prototipo de diseño aún dice «Investia AI»; en todo lo que generes usa Kairox AI).

El repositorio **ya existe** en GitHub: https://github.com/dsmaurod-gif/Kairox_AI.git. Trabaja dentro de su clon local: no hagas `git init`, no cambies el remoto `origin` y no sobrescribas sin preguntarme lo que ya traiga (README, LICENSE, `.gitignore`).

Tu tarea: construir el repositorio público, la app web en Streamlit y las pruebas que demuestran que la app usa **el mismo modelo que se evaluó**. Código, comentarios, interfaz y documentos en español, tono académico y formal.

## 2. Reglas que no se rompen
1. No reentrenar, no ajustar hiperparámetros, no cambiar el umbral ni las fórmulas. El modelo es un archivo fijo.
2. El conjunto de prueba ya se usó una sola vez. Aquí solo se lee para (a) la prueba de integridad y (b) elegir 3 casos de ejemplo con la regla de la sección 6.6. Nunca para decidir nada del modelo.
3. No inventes cifras. Si un número no coincide con los de la sección 8, **detente, repórtalo y no lo "arregles"**.
4. El puntaje NO es una probabilidad (SMOTE equilibró las clases al entrenar; no está calibrado). Nunca lo muestres como porcentaje ni lo llames "probabilidad". Escala 0–1 con dos decimales y umbral 0.50.
5. No prometas exactitud ni escribas frases como "decisiones más seguras". Cifras reales permitidas en la interfaz: F1 0.205 (IC 95 %: 0.170–0.238), recall 0.388 (0.334–0.443), precisión 0.139, PR-AUC 0.135 (referencia sin capacidad predictiva: 0.067), umbral 0.50. La meta de F1 0.80 es una aspiración no alcanzada.
6. No subas al repositorio los `dataset_*.csv`, credenciales ni metadatos de cuenta de Google de los cuadernos.
7. Trabaja por etapas (sección 9): al terminar cada una haz commit local, **no hagas push** (el push lo hago yo, a mano) y espera mi revisión. Nunca `git push --force`.
8. Si una decisión no está aquí, pregunta antes de decidir.
9. Usa siempre el intérprete de `.venv/`; no instales nada fuera de `requirements*.txt` sin preguntarme; no borres archivos ni ejecutes comandos destructivos; no leas ni muestres credenciales.
10. Al iniciar una conversación nueva, lee `docs/avance.md` y `git log` para retomar donde quedó el trabajo.

## 3. Archivos de entrada
Los entrego yo y van en `datos_locales/` (ignorada por git). Los marcados con ✔ se copian además al repositorio.

| Archivo | Contenido |
|---|---|
| `modelo_final.joblib` ✔ (24.08 MB, en `models/`) | Pipeline imblearn: `imputacion` → `winsorizacion` → `escalado` → `smote` → `modelo`. |
| `modelo_final_metadatos.json` ✔ | `variables` (orden de las 17 columnas), `umbral_decision` (0.50), hiperparámetros, semilla 42. |
| `parametros_modelo.json` ✔ | `mediana_imputacion`, `limite_inferior`, `limite_superior` por variable; `activo_total_equivalente_millones` {p1, mediana, p99}. |
| `versiones_entorno.json` ✔ | Versiones con las que carga el modelo sin advertencias. |
| `proba_prueba.npy` | Puntajes del modelo sobre la prueba (15,742 observaciones), calculados una sola vez. Orden esperado = filas de `dataset_prueba.csv` **[verificar longitud y orden; si hay 2 columnas, usar la de la clase 1]**. |
| `dataset_elaborado.csv` | `empresa`, `anio`, 18 cifras originales, ratios y `riesgo_critico` (78,682 filas). |
| `dataset_filtrado.csv` | `empresa`, `anio`, las 17 variables del modelo y `riesgo_critico`. |
| `dataset_prueba.csv` | Conjunto de prueba: 1,794 empresas, 15,742 observaciones **[verificar columnas]**. |

## 4. Entorno
Python 3.11 o superior [completar versión usada]. `requirements.txt` con versiones fijas: `scikit-learn==1.6.1`, `imbalanced-learn==0.14.2`, `joblib==1.6.0`, `pandas==2.2.3`, `numpy` (Colab usó 2.4.6; si no instala, relaja y avísame), `streamlit` (fija la versión estable que instales y anótala). `requirements-dev.txt`: `pytest`. **scikit-learn debe ser exactamente 1.6.1**: el `.joblib` es sensible a la versión. Un modelo cargado sin aviso de versión es la señal de que el entorno es correcto (en Colab solo salió un aviso ajeno de `datetime.utcnow`).

## 5. Estructura del repositorio
```
Kairox_AI/
├── README.md  CLAUDE.md  LICENSE [completar]  requirements.txt  requirements-dev.txt  .gitignore
├── .streamlit/config.toml            # tema (sección 10)
├── app/app.py
├── src/kairox/{__init__,transformadores,indicadores,modelo,validaciones,explicacion,ejemplos}.py
├── models/                           # modelo, metadatos, parámetros, versiones
├── data/{ejemplos_prueba.csv,plantilla_empresa.csv,README_datos.md}
├── scripts/{seleccionar_ejemplos.py,verificar_integridad.py,limpiar_cuaderno.py}
├── notebooks/                        # cuadernos sin metadatos de cuenta
├── tests/
├── docs/{guia_estilo.md,arquitectura.md,declaracion_uso_ia.md}
└── reports/pruebas_7_1_3.md
```
`data/README_datos.md`: el dataset completo no se incluye (enlace a Kaggle; licencia [completar]). `app/app.py` agrega `src/` a `sys.path` (sin `pip install -e .`).

## 6. Especificación de los módulos

### 6.1 `transformadores.py`
Copia **tal cual** (el modelo guardado la necesita):
```python
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class Winsorizador(BaseEstimator, TransformerMixin):
    def __init__(self, inferior=0.01, superior=0.99):
        self.inferior = inferior
        self.superior = superior
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.lim_inf_ = np.nanquantile(X, self.inferior, axis=0)
        self.lim_sup_ = np.nanquantile(X, self.superior, axis=0)
        return self
    def transform(self, X):
        return np.clip(np.asarray(X, dtype=float), self.lim_inf_, self.lim_sup_)
```

### 6.2 `modelo.py`
- `cargar_modelo()` → `(pipeline, metadatos, parametros)`. **Antes de `joblib.load`**: `sys.modules['__main__'].Winsorizador = Winsorizador` (el archivo se guardó con la clase definida en `__main__` de Colab). Comenta el motivo. En la app, envolver con `st.cache_resource`.
- `puntuar(df)`: recibe un DataFrame con las 17 columnas **en el orden de `metadatos['variables']`** (no lo escribas a mano) y devuelve `predict_proba(df)[:, 1]`. Verifica que no aparezcan avisos de nombres de columnas.
- `clasificar(puntaje, umbral)`: riesgo crítico si `puntaje >= umbral` (umbral de `metadatos['umbral_decision']`). La prueba de integridad decide si el criterio es `>=` o `>`: debe reproducir los conteos de la sección 8; si ninguno coincide, detente.
- `importancias()`: `feature_importances_` del paso `modelo`, en %, 1 decimal.

### 6.3 `indicadores.py`
`calcular_variables(cifras)` → DataFrame de 1 o más filas con las 17 columnas del modelo, a partir de las **16 cifras de entrada**. Regla de división: denominador 0 → `NaN` (nunca infinito); `NaN` en la entrada → `NaN` en la salida (el pipeline los imputa con la mediana). Ya verificado contra el entrenamiento (diferencia máxima ≤ 4e-12, mismos NaN).

| Variable | Etiqueta | Fórmula | Qué mide (texto de la interfaz) |
|---|---|---|---|
| `liquidez_corriente` | Liquidez corriente | activo_corriente / pasivo_corriente | Mide si la empresa puede pagar sus deudas de corto plazo con lo que tiene a corto plazo. |
| `prueba_acida` | Prueba ácida | (activo_corriente − inventario) / pasivo_corriente | Igual que la liquidez corriente, pero sin contar el inventario, que tarda en convertirse en dinero. |
| `capital_trabajo_activos` | Capital de trabajo / activos | (activo_corriente − pasivo_corriente) / activo_total | Colchón de corto plazo en relación con el tamaño de la empresa. |
| `endeudamiento` | Endeudamiento | pasivo_total / activo_total | Qué parte de lo que posee la empresa está financiada con deuda. |
| `deuda_lp_activos` | Deuda de largo plazo / activos | deuda_largo_plazo / activo_total | Peso de las deudas de largo plazo sobre los activos. |
| `utilidades_retenidas_activos` | Utilidades retenidas / activos | utilidades_retenidas / activo_total | Ganancias acumuladas que la empresa conservó, en relación con sus activos. |
| `ebit_activos` | EBIT / activos | ebit / activo_total | Ganancia operativa (antes de intereses e impuestos) que generan los activos. |
| `roa` | ROA | utilidad_neta / activo_total | Ganancia final que produce cada unidad de activo. |
| `margen_bruto` | Margen bruto | utilidad_bruta / ingresos_totales | Parte de cada ingreso que queda después de los costos directos. |
| `margen_ebitda` | Margen EBITDA | ebitda / ingresos_totales | Ganancia operativa antes de depreciaciones, en relación con los ingresos. |
| `margen_neto` | Margen neto | utilidad_neta / ingresos_totales | Parte de cada ingreso que se convierte en ganancia final. |
| `valor_mercado_pasivos` | Valor de mercado / pasivos | valor_mercado / pasivo_total | Cuántas veces el valor de la empresa en bolsa cubre sus deudas. |
| `rotacion_activos` | Rotación de activos | ingresos_totales / activo_total | Cuántas ventas genera cada unidad de activo. |
| `gastos_operativos_ingresos` | Gastos operativos / ingresos | gastos_operativos / ingresos_totales | Parte de los ingresos que consumen los gastos de operar. |
| `rotacion_cuentas_cobrar` | Rotación de cuentas por cobrar | ingresos_totales / cuentas_por_cobrar | Qué tan rápido la empresa cobra lo que vende a crédito. |
| `crecimiento_ingresos` | Crecimiento de ingresos | (ingresos_totales − ingresos_anio_anterior) / \|ingresos_anio_anterior\| | Cuánto crecieron o cayeron los ingresos frente al año previo. |
| `tamano_empresa` | Tamaño de la empresa | log1p(max(activo_total, 0)) | Tamaño de la empresa en escala logarítmica. |

En el entrenamiento `ventas_netas` e `ingresos_totales` son columnas **idénticas** (comprobado), por eso la app pide una sola cifra de ingresos.

### 6.4 `validaciones.py`
`validar_cifras(cifras)` → `{bloqueos: [...], avisos: [...]}`; `leer_csv(archivo)` → cifras de la **primera fila**.
- **Bloqueos:** activo_total ausente o ≤ 0 («El activo total debe ser mayor que cero: de él dependen casi todos los indicadores.»); menos de 9 de 16 cifras («Con menos de 9 cifras el análisis no es confiable (criterio de diseño del sistema).» — es un criterio de diseño, no empírico).
- **Avisos:** «Faltan N de 16 cifras. Los indicadores que dependen de ellas se imputarán con la mediana y el resultado será menos confiable.»; activo_corriente > activo_total; pasivo_total < 0; ingresos_totales ausente o 0; ingresos_anio_anterior ausente («el crecimiento de ingresos queda sin dato»).
- **Escala** (límites de `parametros_modelo.json`, no los escribas a mano): activo_total fuera de [p1, p99] → «Fuera del rango de entrenamiento: el modelo recorta este valor»; activo_total > 1,000,000 → «Posible error de unidades: las cifras deben estar en millones de dólares». Son avisos, no bloqueos.
- **CSV:** encabezados en minúscula, separador `,` o `;` (con `;` se acepta coma decimal), solo la primera fila (avisar si hay más), valores no numéricos → mensaje claro, nunca una excepción.

### 6.5 `explicacion.py` (RNF02)
Sensibilidad individual: sea `s0` el puntaje de la empresa; para cada una de las 17 variables, reemplázala por su mediana de entrenamiento (`mediana_imputacion`) y recalcula; `efecto_j = s0 − s_j`. Muestra las 5 con mayor |efecto|, con el signo («sube el puntaje» / «baja el puntaje») y el valor de la empresa. Calcula las 17 variantes en **un solo** `predict_proba`. Una variable sin dato tiene efecto 0 por construcción: indícalo como «sin dato». Texto obligatorio: «Aproximación: compara cada variable con la empresa típica del entrenamiento, una a la vez. No prueba causalidad ni recoge interacciones.»

### 6.6 `ejemplos.py` y `scripts/seleccionar_ejemplos.py`
Tres casos reales del **conjunto de prueba** → `data/ejemplos_prueba.csv` (columnas: `caso`, `tipo`, `empresa`, `anio`, las 16 cifras, `riesgo_real`, `puntaje_referencia` = valor de `proba_prueba.npy`). Tipos: **acierto** (riesgo real 1 y puntaje ≥ umbral), **falsa alarma** (riesgo real 0 y puntaje ≥ umbral), **caso no detectado** (riesgo real 1 y puntaje < umbral). Regla fijada de antemano **[propuesta: confirmar conmigo antes de ejecutar]**: entre las observaciones de la categoría con año anterior disponible y activo_total dentro de [p1, p99], elegir la de puntaje más cercano a la mediana de su categoría; desempate por (`empresa`, `anio`). `ingresos_anio_anterior` sale de `groupby('empresa')['ingresos_totales'].shift(1)` sobre `dataset_elaborado.csv`. Rótulo en la interfaz: «Caso elegido para mostrar un acierto / una falsa alarma / un caso no detectado; no representa el desempeño general.» Tras analizar, mostrar «Lo que ocurrió: la empresa quebró / no quebró».

## 7. Especificación de la app (`app/app.py`)
Nombre visible: **Kairox AI** (título de la pestaña, cabecera y pie). Flujo de 2 pasos (1 Datos → 2 Resultado), en una sola página, legible en celular.
- **Aviso de alcance** (reutilizar): «Para qué sirve y para qué no. Responde una sola pregunta: si la empresa es un destino viable para el capital o presenta riesgo crítico. Requiere cifras de al menos un ejercicio contable completo, en millones de dólares, y supone que la información es veraz (no detecta manipulación contable). No define el monto, el momento de entrada ni el tipo de instrumento, y no reemplaza el análisis financiero ni el criterio de quien decide.»
- **Tres métodos:** «Empresa de ejemplo» (Un clic, sin escribir nada: los 3 casos de 6.6); «Subir archivo» (CSV con las cifras de la empresa; plantilla descargable `data/plantilla_empresa.csv` con las 16 columnas y una fila de ejemplo); «Ingresar manualmente» (16 cifras del balance y resultados, en millones de dólares).
- **16 cifras de entrada**, claves y etiquetas: *Balance general* (9): `activo_corriente` Activo corriente, `pasivo_corriente` Pasivo corriente, `inventario` Inventario, `activo_total` Activo total, `pasivo_total` Pasivo total, `deuda_largo_plazo` Deuda de largo plazo, `utilidades_retenidas` Utilidades retenidas, `cuentas_por_cobrar` Cuentas por cobrar, `valor_mercado` Valor de mercado. *Estado de resultados* (7): `ingresos_totales` Ingresos totales (equivale a ventas netas en los datos de entrenamiento), `ingresos_anio_anterior` Ingresos del año anterior, `utilidad_bruta` Utilidad bruta, `ebitda` EBITDA, `ebit` EBIT, `utilidad_neta` Utilidad neta, `gastos_operativos` Gastos operativos. (No confundir: el modelo tiene 17 variables; el usuario escribe 16 cifras.)
- Panel **«Indicadores calculados»** en vivo (17; «—» si falta el dato) con la nota: «Un indicador sin dato (—) se reemplaza con la mediana del entrenamiento. Los valores extremos se recortan a los percentiles 1 % y 99 % observados al entrenar. Si es el primer año, el crecimiento de ingresos queda sin dato.»
- Bloqueos y avisos (6.4) visibles antes de pulsar **«Analizar empresa»**; con bloqueos el botón no analiza.
- **Resultado:** anillo con el puntaje `0.xx` y «Puntaje de riesgo»; etiqueta «Riesgo crítico» / «Inversión viable»; barra de 0.00 a 1.00 con la marca «Umbral 0.50»; texto («El puntaje supera el umbral de 0.50. Conviene revisar con detalle la situación financiera antes de invertir.» / «El puntaje se ubica por debajo del umbral de 0.50. Esto no garantiza que la inversión sea segura.»).
- **Explicación individual** (6.5) y **«Variables que más usa el modelo»** (`importancias()`, importancia global, 5 primeras con el valor de la empresa).
- **«Cómo leer este resultado»**: (1) «El puntaje indica riesgo relativo; no es la probabilidad real de que la empresa quiebre, porque SMOTE equilibra las clases y la probabilidad no está calibrada.» (2) «Una clasificación de riesgo crítico es una alerta para revisar la empresa, no una conclusión.» (3) «En la prueba con empresas que no vio al entrenar, el modelo detectó 4 de cada 10 observaciones de riesgo y solo una de cada siete alertas fue real (F1 0.205, lejos de la aspiración de 0.80).» (4) «Las cifras que se ingresan se suponen veraces y completas; si faltan datos, se imputan con la mediana y el resultado es menos confiable.» (5) «El análisis no define cuánto ni cuándo invertir, y no sustituye el criterio profesional.»
- **Glosario** de los 17 indicadores (tabla de 6.3) y sección «Modelo» con las métricas reales permitidas (regla 5).
- Registrar en pantalla el tiempo de cálculo de la última predicción (RNF03).

## 8. Cifras de referencia (criterios de aceptación)
Prueba, umbral 0.50: 15,742 observaciones de 1,794 empresas; 1,049 observaciones de riesgo; **407 detectadas**; **2,516 falsas alarmas**; F1 0.205, recall 0.388, precisión 0.139, PR-AUC 0.135. Importancias: deuda_lp_activos 10.5 %, tamano_empresa 8.8 %, valor_mercado_pasivos 7.3 %, margen_bruto 7.1 %, margen_neto 6.5 % (suman 40.2 %); la última, liquidez_corriente ≈ 3.7 %. Tiempo de clasificación medido en Colab: mediana 0.068 s, máximo 0.083 s (límite 5 s).

## 9. Etapas (commit local al final de cada una; entrega: resumen de 3 líneas + salida cruda de las pruebas + dudas)
0. Entorno: revisa el estado del clon (`git status`, `git remote -v`, `git log --oneline`) y lo que ya trae. El `.gitignore` ya lo puse yo al clonar: comprueba que ignore `datos_locales/`, `dataset_*.csv`, `proba_prueba.npy`, `.venv/`, `__pycache__/`, `.ipynb_checkpoints/` y, si falta algo, propónmelo; confirma con `git status` que `datos_locales/` no aparece **antes del primer commit**; `docs/avance.md` (registro de etapas, decisiones y salidas crudas; actualízalo al cerrar cada etapa); venv en `.venv/`; `requirements.txt`; comprobar scikit-learn 1.6.1 y que el modelo carga sin avisos de versión.
1. Estructura, `transformadores.py`, `indicadores.py` y `tests/test_indicadores.py` (variables recalculadas desde `dataset_elaborado.csv` vs `dataset_filtrado.csv`: diferencia máxima ≤ 1e-9 y mismos NaN; casos borde: denominador 0, primer año, activo_total ≤ 0).
2. `modelo.py`, `scripts/verificar_integridad.py` y `tests/test_integridad.py`: aplicar el código del repositorio a las 15,742 observaciones de prueba y comparar con `proba_prueba.npy` (diferencia máxima ≤ 1e-9); reproducir 407, 2,516, F1, recall, precisión; comprobar las 5 primeras importancias de la sección 8 e imprimir la tabla **completa** de importancias (17 variables, %, 1 decimal), guardada en `reports/importancias_modelo.csv`. **Si falla, detenerte y reportar.**
3. `validaciones.py`, `explicacion.py`, `tests/test_validaciones.py` (RNF04: entradas inválidas dan mensajes, no excepciones; el mismo dato da exactamente el mismo puntaje en 100 llamadas) y `tests/test_rendimiento.py` (RNF03: mediana y máximo de 100 llamadas de `puntuar` + `explicacion`).
4. Ejemplos: script, `data/ejemplos_prueba.csv`, plantilla y `tests/test_ejemplos.py` (corre sin los datasets: el puntaje recalculado debe igualar `puntaje_referencia`).
5. `app/app.py` y `.streamlit/config.toml`; ejecutar `streamlit run app/app.py`, probar los 3 métodos y pantalla estrecha; describir lo observado.
6. `README.md` (qué es, cómo ejecutar, estructura, cifras reales, limitaciones, declaración de uso de IA [completar herramientas], licencia [completar], equipo [completar]), `docs/`, `scripts/limpiar_cuaderno.py` (elimina `executionInfo.user` y verifica que no queden `displayName`, `userId` ni correos) y `reports/pruebas_7_1_3.md` con las salidas crudas, sin interpretarlas.
7. (Humana) push, despliegue y pruebas en la app desplegada.

## 10. Estilo visual (`docs/guia_estilo.md` y `.streamlit/config.toml`)
Tipografías: Plus Jakarta Sans (texto y títulos, 400–800) y JetBrains Mono (cifras). Colores: primario `#5B3DB5` (hover `#47299A`); acento `#8A64DB` (solo títulos grandes y gráficos); fondos `#EDE6FB`, `#F1ECFB`, `#F8F5FE`; bordes `#E9E1F8`, `#CDBEF0`; texto `#1B1340` (secundario `#4A4568`, `#5A5578`, `#6B6688`); riesgo fondo `#FBE3E8`, texto `#8E1F3A`, barra `#A12A47`; viable fondo `#DDF3E1`, texto `#17612F`; avisos fondo `#FFF6DC`, borde `#F1DFA3`, texto `#5C4707`. Tarjetas con radio 18–24 px, botones 12–14 px; controles de al menos 44 px; foco visible de 3 px en `#8A64DB`. La app reproduce el flujo y el aspecto del prototipo, sin necesidad de coincidir al píxel.
