"""Cálculo de los 17 indicadores del modelo a partir de las 16 cifras de entrada.

Regla de división: denominador 0 -> NaN (nunca infinito); NaN en la entrada -> NaN
en la salida (el pipeline del modelo los imputa con la mediana de entrenamiento).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RUTA_METADATOS = RAIZ / "models" / "modelo_final_metadatos.json"

# Orden de las 17 columnas: se lee de los metadatos del modelo, no se escribe a mano.
with open(RUTA_METADATOS, encoding="utf-8") as _f:
    VARIABLES_MODELO = list(json.load(_f)["variables"])

# Las 16 cifras que escribe el usuario (millones de dólares), por bloque.
CIFRAS_BALANCE = [
    "activo_corriente", "pasivo_corriente", "inventario", "activo_total", "pasivo_total",
    "deuda_largo_plazo", "utilidades_retenidas", "cuentas_por_cobrar", "valor_mercado",
]
CIFRAS_RESULTADOS = [
    "ingresos_totales", "ingresos_anio_anterior", "utilidad_bruta", "ebitda", "ebit",
    "utilidad_neta", "gastos_operativos",
]
CIFRAS_ENTRADA = CIFRAS_BALANCE + CIFRAS_RESULTADOS

ETIQUETAS_CIFRAS = {
    "activo_corriente": "Activo corriente", "pasivo_corriente": "Pasivo corriente",
    "inventario": "Inventario", "activo_total": "Activo total", "pasivo_total": "Pasivo total",
    "deuda_largo_plazo": "Deuda de largo plazo", "utilidades_retenidas": "Utilidades retenidas",
    "cuentas_por_cobrar": "Cuentas por cobrar", "valor_mercado": "Valor de mercado",
    "ingresos_totales": "Ingresos totales", "ingresos_anio_anterior": "Ingresos del año anterior",
    "utilidad_bruta": "Utilidad bruta", "ebitda": "EBITDA", "ebit": "EBIT",
    "utilidad_neta": "Utilidad neta", "gastos_operativos": "Gastos operativos",
}

# variable: (etiqueta, fórmula legible, qué mide)
INDICADORES = {
    "liquidez_corriente": ("Liquidez corriente", "activo_corriente / pasivo_corriente",
        "Mide si la empresa puede pagar sus deudas de corto plazo con lo que tiene a corto plazo."),
    "prueba_acida": ("Prueba ácida", "(activo_corriente − inventario) / pasivo_corriente",
        "Igual que la liquidez corriente, pero sin contar el inventario, que tarda en convertirse en dinero."),
    "capital_trabajo_activos": ("Capital de trabajo / activos", "(activo_corriente − pasivo_corriente) / activo_total",
        "Colchón de corto plazo en relación con el tamaño de la empresa."),
    "endeudamiento": ("Endeudamiento", "pasivo_total / activo_total",
        "Qué parte de lo que posee la empresa está financiada con deuda."),
    "deuda_lp_activos": ("Deuda de largo plazo / activos", "deuda_largo_plazo / activo_total",
        "Peso de las deudas de largo plazo sobre los activos."),
    "utilidades_retenidas_activos": ("Utilidades retenidas / activos", "utilidades_retenidas / activo_total",
        "Ganancias acumuladas que la empresa conservó, en relación con sus activos."),
    "ebit_activos": ("EBIT / activos", "ebit / activo_total",
        "Ganancia operativa (antes de intereses e impuestos) que generan los activos."),
    "roa": ("ROA", "utilidad_neta / activo_total",
        "Ganancia final que produce cada unidad de activo."),
    "margen_bruto": ("Margen bruto", "utilidad_bruta / ingresos_totales",
        "Parte de cada ingreso que queda después de los costos directos."),
    "margen_ebitda": ("Margen EBITDA", "ebitda / ingresos_totales",
        "Ganancia operativa antes de depreciaciones, en relación con los ingresos."),
    "margen_neto": ("Margen neto", "utilidad_neta / ingresos_totales",
        "Parte de cada ingreso que se convierte en ganancia final."),
    "valor_mercado_pasivos": ("Valor de mercado / pasivos", "valor_mercado / pasivo_total",
        "Cuántas veces el valor de la empresa en bolsa cubre sus deudas."),
    "rotacion_activos": ("Rotación de activos", "ingresos_totales / activo_total",
        "Cuántas ventas genera cada unidad de activo."),
    "gastos_operativos_ingresos": ("Gastos operativos / ingresos", "gastos_operativos / ingresos_totales",
        "Parte de los ingresos que consumen los gastos de operar."),
    "rotacion_cuentas_cobrar": ("Rotación de cuentas por cobrar", "ingresos_totales / cuentas_por_cobrar",
        "Qué tan rápido la empresa cobra lo que vende a crédito."),
    "crecimiento_ingresos": ("Crecimiento de ingresos",
        "(ingresos_totales − ingresos_anio_anterior) / |ingresos_anio_anterior|",
        "Cuánto crecieron o cayeron los ingresos frente al año previo."),
    "tamano_empresa": ("Tamaño de la empresa", "log1p(max(activo_total, 0))",
        "Tamaño de la empresa en escala logarítmica."),
}


def _dividir(numerador, denominador):
    """División con denominador 0 -> NaN (nunca infinito); NaN se propaga."""
    return numerador / denominador.where(denominador != 0)


def _como_dataframe(cifras):
    """Acepta un dict (valores escalares o listas) o un DataFrame con las 16 cifras."""
    if isinstance(cifras, pd.DataFrame):
        df = cifras.copy()
    elif all(np.isscalar(v) or v is None for v in cifras.values()):
        df = pd.DataFrame([cifras])
    else:
        df = pd.DataFrame(cifras)
    for col in CIFRAS_ENTRADA:
        if col not in df.columns:
            df[col] = np.nan  # cifra ausente -> NaN
    return df[CIFRAS_ENTRADA].apply(pd.to_numeric, errors="coerce").astype(float)


def calcular_variables(cifras):
    """Devuelve un DataFrame (1 o más filas) con las 17 variables del modelo."""
    c = _como_dataframe(cifras)
    v = pd.DataFrame(index=c.index)
    v["liquidez_corriente"] = _dividir(c.activo_corriente, c.pasivo_corriente)
    v["prueba_acida"] = _dividir(c.activo_corriente - c.inventario, c.pasivo_corriente)
    v["capital_trabajo_activos"] = _dividir(c.activo_corriente - c.pasivo_corriente, c.activo_total)
    v["endeudamiento"] = _dividir(c.pasivo_total, c.activo_total)
    v["deuda_lp_activos"] = _dividir(c.deuda_largo_plazo, c.activo_total)
    v["utilidades_retenidas_activos"] = _dividir(c.utilidades_retenidas, c.activo_total)
    v["ebit_activos"] = _dividir(c.ebit, c.activo_total)
    v["roa"] = _dividir(c.utilidad_neta, c.activo_total)
    v["margen_bruto"] = _dividir(c.utilidad_bruta, c.ingresos_totales)
    v["margen_ebitda"] = _dividir(c.ebitda, c.ingresos_totales)
    v["margen_neto"] = _dividir(c.utilidad_neta, c.ingresos_totales)
    v["valor_mercado_pasivos"] = _dividir(c.valor_mercado, c.pasivo_total)
    v["rotacion_activos"] = _dividir(c.ingresos_totales, c.activo_total)
    v["gastos_operativos_ingresos"] = _dividir(c.gastos_operativos, c.ingresos_totales)
    v["rotacion_cuentas_cobrar"] = _dividir(c.ingresos_totales, c.cuentas_por_cobrar)
    v["crecimiento_ingresos"] = _dividir(c.ingresos_totales - c.ingresos_anio_anterior,
                                         c.ingresos_anio_anterior.abs())
    v["tamano_empresa"] = np.log1p(c.activo_total.clip(lower=0))  # NaN se conserva
    return v[VARIABLES_MODELO]
