"""Casos de ejemplo (reales, del conjunto de prueba) y plantilla de empresa."""
from pathlib import Path

import pandas as pd

from kairox.indicadores import CIFRAS_ENTRADA

RAIZ = Path(__file__).resolve().parents[2]
RUTA_EJEMPLOS = RAIZ / "data" / "ejemplos_prueba.csv"
RUTA_PLANTILLA = RAIZ / "data" / "plantilla_empresa.csv"

ROTULOS = {
    "acierto": "Caso elegido para mostrar un acierto; no representa el desempeño general.",
    "falsa alarma": "Caso elegido para mostrar una falsa alarma; no representa el desempeño general.",
    "caso no detectado": "Caso elegido para mostrar un caso no detectado; no representa el desempeño general.",
}


def cargar_ejemplos():
    """DataFrame con los 3 casos (columnas: caso, tipo, empresa, anio, 16 cifras, riesgo_real, puntaje_referencia)."""
    # round_trip: el lector rápido de pandas puede alterar el último bit de un decimal.
    return pd.read_csv(RUTA_EJEMPLOS, float_precision="round_trip")


def cifras_de(fila):
    """Las 16 cifras de un caso como diccionario."""
    return {c: float(fila[c]) for c in CIFRAS_ENTRADA}


def rotulo(tipo):
    return ROTULOS[tipo]


def lo_que_ocurrio(riesgo_real):
    """Texto posterior al análisis."""
    return "Lo que ocurrió: la empresa quebró" if int(riesgo_real) == 1 else "Lo que ocurrió: la empresa no quebró"


def contenido_plantilla():
    """Bytes de la plantilla descargable (16 columnas y una fila de ejemplo)."""
    return RUTA_PLANTILLA.read_bytes()
