"""Carga y uso del modelo final (Random Forest dentro de un pipeline de imblearn).

El modelo es un archivo fijo: aquí no se reentrena ni se ajusta nada.
"""
import json
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from kairox.transformadores import Winsorizador

RAIZ = Path(__file__).resolve().parents[2]
CARPETA_MODELOS = RAIZ / "models"

# Criterio de clasificación: riesgo crítico si puntaje >= umbral. Lo confirma la
# prueba de integridad (scripts/verificar_integridad.py), que debe reproducir los
# conteos de la sección 8 de CLAUDE.md.
CRITERIO = ">="


def cargar_modelo():
    """Devuelve (pipeline, metadatos, parametros)."""
    # El archivo .joblib se guardó en Colab con la clase Winsorizador definida en
    # __main__; para deserializarlo hay que exponerla allí antes de joblib.load.
    sys.modules["__main__"].Winsorizador = Winsorizador
    pipeline = joblib.load(CARPETA_MODELOS / "modelo_final.joblib")
    # El bosque se guardó con n_jobs=-1: la suma de los 300 árboles en varios hilos
    # cambia de orden entre llamadas y el puntaje varía en el último bit (~3e-17).
    # Con n_jobs=1 el mismo dato da exactamente el mismo puntaje (RNF04). Es un ajuste
    # en memoria de ejecución, no un hiperparámetro del modelo: el archivo no cambia.
    pipeline.named_steps["modelo"].n_jobs = 1
    with open(CARPETA_MODELOS / "modelo_final_metadatos.json", encoding="utf-8") as f:
        metadatos = json.load(f)
    with open(CARPETA_MODELOS / "parametros_modelo.json", encoding="utf-8") as f:
        parametros = json.load(f)
    return pipeline, metadatos, parametros


def puntuar(df, pipeline=None, metadatos=None):
    """Puntaje de riesgo (0-1, no calibrado) = predict_proba(df)[:, 1].

    `df` debe traer las 17 columnas en el orden de metadatos['variables'].
    """
    if pipeline is None or metadatos is None:
        pipeline, metadatos, _ = cargar_modelo()
    variables = list(metadatos["variables"])
    if list(df.columns) != variables:
        raise ValueError("Las columnas deben ser exactamente las 17 variables del modelo, "
                         "en el orden de metadatos['variables'].")
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always")
        puntajes = pipeline.predict_proba(df)[:, 1]
    for a in avisos:
        if "feature names" in str(a.message):
            raise RuntimeError(f"Aviso de nombres de columnas: {a.message}")
    return puntajes


def clasificar(puntaje, umbral=None, metadatos=None):
    """True (riesgo crítico) si puntaje >= umbral; admite escalares o arreglos."""
    if umbral is None:
        if metadatos is None:
            metadatos = cargar_modelo()[1]
        umbral = metadatos["umbral_decision"]
    puntaje = np.asarray(puntaje, dtype=float)
    return puntaje >= umbral if CRITERIO == ">=" else puntaje > umbral


def importancias(pipeline=None, metadatos=None):
    """Importancia global (feature_importances_ del paso 'modelo') en %, 1 decimal."""
    if pipeline is None or metadatos is None:
        pipeline, metadatos, _ = cargar_modelo()
    valores = pipeline.named_steps["modelo"].feature_importances_
    variables = list(metadatos["variables"])
    if len(valores) != len(variables):
        raise ValueError("El número de importancias no coincide con las variables.")
    serie = pd.Series(np.round(valores * 100, 1), index=variables, name="importancia_pct")
    return serie.sort_values(ascending=False, kind="stable")
