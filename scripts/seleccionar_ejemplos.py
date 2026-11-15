"""Selecciona 3 casos reales del conjunto de prueba -> data/ejemplos_prueba.csv.

Regla fijada de antemano (CLAUDE.md, 6.6), aprobada por el responsable:
  - Categorías: acierto (riesgo real 1 y puntaje >= umbral), falsa alarma (riesgo real 0 y
    puntaje >= umbral) y caso no detectado (riesgo real 1 y puntaje < umbral).
  - La mediana del puntaje se calcula sobre TODAS las observaciones de la categoría
    (si el número es par: promedio de los dos centrales).
  - Representante: entre las observaciones de la categoría con año anterior disponible y
    activo_total dentro de [p1, p99], la de puntaje más cercano a esa mediana;
    desempate por (empresa, anio).
El conjunto de prueba solo se LEE aquí; no se usa para decidir nada sobre el modelo.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from kairox.indicadores import CIFRAS_ENTRADA  # noqa: E402

DATOS = RAIZ / "datos_locales"
SALIDA = RAIZ / "data" / "ejemplos_prueba.csv"
TIPOS = ["acierto", "falsa alarma", "caso no detectado"]
COLUMNAS = ["caso", "tipo", "empresa", "anio"] + CIFRAS_ENTRADA + ["riesgo_real", "puntaje_referencia"]


def seleccionar():
    with open(RAIZ / "models" / "modelo_final_metadatos.json", encoding="utf-8") as f:
        umbral = json.load(f)["umbral_decision"]
    with open(RAIZ / "models" / "parametros_modelo.json", encoding="utf-8") as f:
        equiv = json.load(f)["activo_total_equivalente_millones"]
    p1, p99 = equiv["p1"], equiv["p99"]

    prueba = pd.read_csv(DATOS / "dataset_prueba.csv")
    puntajes = np.load(DATOS / "proba_prueba.npy")
    if puntajes.ndim == 2:
        puntajes = puntajes[:, 1]
    assert len(prueba) == len(puntajes) == 15742
    prueba["puntaje_referencia"] = puntajes
    prueba["riesgo_real"] = prueba["riesgo_critico"]

    elab = pd.read_csv(DATOS / "dataset_elaborado.csv").sort_values(["empresa", "anio"], kind="stable")
    elab["ingresos_anio_anterior"] = elab.groupby("empresa")["ingresos_totales"].shift(1)
    prueba = prueba.merge(elab[["empresa", "anio", "ingresos_anio_anterior"]],
                          on=["empresa", "anio"], how="left", validate="one_to_one")

    real, pun = prueba["riesgo_real"], prueba["puntaje_referencia"]
    categorias = {
        "acierto": (real == 1) & (pun >= umbral),
        "falsa alarma": (real == 0) & (pun >= umbral),
        "caso no detectado": (real == 1) & (pun < umbral),
    }
    elegible = prueba["ingresos_anio_anterior"].notna() & prueba["activo_total"].between(p1, p99)

    filas = []
    for numero, tipo in enumerate(TIPOS, start=1):
        cat = prueba[categorias[tipo]]
        mediana = float(cat["puntaje_referencia"].median())  # par: promedio de los dos centrales
        cand = prueba[categorias[tipo] & elegible].copy()
        if cand.empty:
            raise SystemExit(f"Sin candidatas para la categoría «{tipo}»")
        cand["distancia"] = (cand["puntaje_referencia"] - mediana).abs()
        elegido = cand.sort_values(["distancia", "empresa", "anio"], kind="stable").iloc[0]
        print(f"{tipo}: {len(cat)} observaciones, {len(cand)} elegibles, mediana {mediana:.6f} "
              f"-> {elegido['empresa']} {int(elegido['anio'])} (puntaje {elegido['puntaje_referencia']:.6f})")
        fila = {"caso": numero, "tipo": tipo, "empresa": elegido["empresa"], "anio": int(elegido["anio"])}
        fila.update({c: float(elegido[c]) for c in CIFRAS_ENTRADA})
        fila["riesgo_real"] = int(elegido["riesgo_real"])
        fila["puntaje_referencia"] = float(elegido["puntaje_referencia"])
        filas.append(fila)
    return pd.DataFrame(filas, columns=COLUMNAS)


if __name__ == "__main__":
    ejemplos = seleccionar()
    ejemplos.to_csv(SALIDA, index=False, encoding="utf-8")
    print(f"Escrito: {SALIDA.relative_to(RAIZ)} ({len(ejemplos)} filas)")
