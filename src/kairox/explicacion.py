"""Explicación individual por sensibilidad (RNF02).

Para cada variable se reemplaza su valor por la mediana de entrenamiento y se mide
cuánto cambia el puntaje. Las 17 variantes (más la original) se puntúan en un solo
predict_proba.
"""
import numpy as np
import pandas as pd

from kairox import modelo
from kairox.indicadores import INDICADORES

NOTA_APROXIMACION = ("Aproximación: compara cada variable con la empresa típica del entrenamiento, "
                     "una a la vez. No prueba causalidad ni recoge interacciones.")


def explicar(variables, pipeline, metadatos, parametros, n=5):
    """`variables`: DataFrame de 1 fila con las 17 columnas del modelo.

    Devuelve {'puntaje', 'efectos' (las n con mayor |efecto|), 'nota'}.
    efecto_j = s0 - s_j > 0 -> el valor de la empresa sube el puntaje respecto de la mediana.
    """
    nombres = list(metadatos["variables"])
    fila = variables[nombres].iloc[[0]].astype(float).reset_index(drop=True)
    medianas = parametros["mediana_imputacion"]
    lote = pd.concat([fila] * (len(nombres) + 1), ignore_index=True)
    for j, nombre in enumerate(nombres, start=1):
        lote.loc[j, nombre] = medianas[nombre]
    puntajes = modelo.puntuar(lote, pipeline, metadatos)  # un solo predict_proba
    s0 = float(puntajes[0])
    efectos = []
    for j, nombre in enumerate(nombres, start=1):
        valor = fila.loc[0, nombre]
        sin_dato = bool(np.isnan(valor))
        efecto = 0.0 if sin_dato else float(s0 - puntajes[j])  # sin dato: efecto 0 por construcción
        if sin_dato or efecto == 0:
            direccion = "sin dato" if sin_dato else "sin efecto"
        else:
            direccion = "sube el puntaje" if efecto > 0 else "baja el puntaje"
        efectos.append({"variable": nombre, "etiqueta": INDICADORES[nombre][0],
                        "valor": None if sin_dato else float(valor), "efecto": efecto,
                        "direccion": direccion, "sin_dato": sin_dato})
    efectos.sort(key=lambda e: -abs(e["efecto"]))  # estable: empates en orden de variables
    return {"puntaje": s0, "efectos": efectos[:n], "nota": NOTA_APROXIMACION}
