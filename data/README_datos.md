# Datos

## Origen

Dataset de origen: **American Companies Bankruptcy Prediction Dataset** (Kaggle; Lombardo et al., 2022): 78,682 observaciones anuales de 8,971 empresas (1999–2018).

- Enlace de Kaggle: [completar]
- Licencia del dataset: [completar]

El dataset completo **no se incluye** en este repositorio. Para reproducir los datos hay que obtenerlo del origen indicado.

## Archivos de esta carpeta

| Archivo | Contenido |
|---|---|
| `ejemplos_prueba.csv` | Tres casos reales del conjunto de prueba (un acierto, una falsa alarma y un caso no detectado) con las 16 cifras de entrada, el riesgo real y el puntaje de referencia. No representan el desempeño general. |
| `plantilla_empresa.csv` | Plantilla descargable desde la app: las 16 columnas y una fila con cifras **ficticias**. |

## Las 16 cifras de entrada (millones de dólares)

Balance general: `activo_corriente`, `pasivo_corriente`, `inventario`, `activo_total`, `pasivo_total`, `deuda_largo_plazo`, `utilidades_retenidas`, `cuentas_por_cobrar`, `valor_mercado`.

Estado de resultados: `ingresos_totales` (equivale a ventas netas en los datos de entrenamiento), `ingresos_anio_anterior`, `utilidad_bruta`, `ebitda`, `ebit`, `utilidad_neta`, `gastos_operativos`.

De ellas se derivan las 17 variables del modelo (16 ratios financieros y `tamano_empresa`).

## Formato del CSV de entrada

Encabezados en minúscula, separador `,` o `;` (con `;` se acepta coma decimal) y una sola fila de datos; si hay más, solo se usa la primera.
