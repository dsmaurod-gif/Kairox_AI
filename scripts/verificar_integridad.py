"""Prueba de integridad: el código del repositorio reproduce la evaluación original.

Uso: python scripts/verificar_integridad.py   (código de salida 1 si algo no coincide)
Solo LEE el conjunto de prueba; no decide nada sobre el modelo.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from kairox import modelo  # noqa: E402
from kairox.indicadores import CIFRAS_ENTRADA, calcular_variables  # noqa: E402

DATOS = RAIZ / "datos_locales"
TOLERANCIA = 1e-9
# Cifras de referencia (sección 8 de CLAUDE.md)
REF = dict(n=15742, empresas=1794, positivos=1049, detectadas=407, falsas_alarmas=2516,
           f1=0.205, recall=0.388, precision=0.139, pr_auc=0.135)
REF_TOP5 = [("deuda_lp_activos", 10.5), ("tamano_empresa", 8.8), ("valor_mercado_pasivos", 7.3),
            ("margen_bruto", 7.1), ("margen_neto", 6.5)]


def archivos_requeridos():
    return [DATOS / n for n in ("dataset_prueba.csv", "dataset_elaborado.csv", "proba_prueba.npy")]


def _diferencias(calculado, referencia):
    d = np.abs(np.asarray(calculado) - np.asarray(referencia))
    return dict(maxima=float(d.max()), n_difieren=int((d > TOLERANCIA).sum()))


def _metricas(y, puntaje, umbral, criterio):
    pred = puntaje >= umbral if criterio == ">=" else puntaje > umbral
    tp = int((pred & (y == 1)).sum())
    fp = int((pred & (y == 0)).sum())
    fn = int((~pred & (y == 1)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return dict(criterio=criterio, detectadas=tp, falsas_alarmas=fp,
                f1=f1, recall=recall, precision=precision)


def ejecutar(guardar=True):
    """Devuelve (resultados, fallos). `fallos` es una lista de textos; vacía = todo coincide."""
    fallos, res = [], {}
    pipeline, metadatos, _ = modelo.cargar_modelo()
    variables = list(metadatos["variables"])
    umbral = metadatos["umbral_decision"]

    prueba = pd.read_csv(DATOS / "dataset_prueba.csv")
    ref = np.load(DATOS / "proba_prueba.npy")
    if ref.ndim == 2:
        ref = ref[:, 1]  # si hay 2 columnas, la de la clase 1
    res["n_observaciones"], res["n_empresas"] = len(prueba), int(prueba["empresa"].nunique())
    if (len(prueba), len(ref)) != (REF["n"], REF["n"]) or res["n_empresas"] != REF["empresas"]:
        fallos.append(f"tamaños distintos: prueba={len(prueba)}, npy={len(ref)}, "
                      f"empresas={res['n_empresas']}")
        return res, fallos
    y = prueba["riesgo_critico"].to_numpy()

    # (a) Variables ya calculadas en dataset_prueba.csv
    puntaje_a = modelo.puntuar(prueba[variables], pipeline, metadatos)
    res["a"] = _diferencias(puntaje_a, ref)

    # (b) Recalcular las variables desde las cifras con indicadores.py. El año anterior
    # sale de dataset_elaborado.csv (grupo por empresa, ordenado por año), porque el
    # conjunto de prueba no contiene necesariamente el año previo de cada observación.
    elab = pd.read_csv(DATOS / "dataset_elaborado.csv").sort_values(["empresa", "anio"], kind="stable")
    elab["ingresos_anio_anterior"] = elab.groupby("empresa")["ingresos_totales"].shift(1)
    primer_anio = ~elab.duplicated("empresa", keep="first")  # primera fila de cada empresa
    cruce = prueba[["empresa", "anio"]].merge(
        elab[["empresa", "anio"] + CIFRAS_ENTRADA].assign(primer_anio=primer_anio.to_numpy()),
        on=["empresa", "anio"], how="left", validate="one_to_one", indicator=True)
    res["b_filas_cruce"] = len(cruce)
    if len(cruce) != REF["n"] or not (cruce["_merge"] == "both").all():
        fallos.append(f"cruce por (empresa, anio): {len(cruce)} filas; "
                      f"{cruce['_merge'].value_counts().to_dict()}")
        return res, fallos
    n_primer = int(cruce["primer_anio"].sum())
    n_nan_prev = int(cruce["ingresos_anio_anterior"].isna().sum())
    res["b_primer_anio"], res["b_nan_ingresos_prev"] = n_primer, n_nan_prev
    if int(cruce.loc[cruce["primer_anio"], "ingresos_anio_anterior"].notna().sum()) != 0:
        fallos.append("hay primeros años con ingresos_anio_anterior no vacío")
    var_b = calcular_variables(cruce[CIFRAS_ENTRADA])
    puntaje_b = modelo.puntuar(var_b[variables], pipeline, metadatos)
    res["b"] = _diferencias(puntaje_b, ref)
    for etiqueta in ("a", "b"):
        if res[etiqueta]["maxima"] > TOLERANCIA:
            fallos.append(f"({etiqueta}) diferencia máxima {res[etiqueta]['maxima']:.3e} > {TOLERANCIA}")

    # Criterio de clasificación y métricas (con el puntaje de referencia del .npy)
    res["positivos"] = int(y.sum())
    if res["positivos"] != REF["positivos"]:
        fallos.append(f"observaciones de riesgo: {res['positivos']} (esperadas {REF['positivos']})")
    res["metricas"] = {c: _metricas(y, ref, umbral, c) for c in (">=", ">")}
    m = res["metricas"][modelo.CRITERIO]
    res["criterio_usado"] = modelo.CRITERIO
    if (m["detectadas"], m["falsas_alarmas"]) != (REF["detectadas"], REF["falsas_alarmas"]):
        fallos.append(f"conteos con '{modelo.CRITERIO}': {m['detectadas']} detectadas y "
                      f"{m['falsas_alarmas']} falsas alarmas (esperados 407 y 2516)")
    for k in ("f1", "recall", "precision"):
        if round(m[k], 3) != REF[k]:
            fallos.append(f"{k}: {m[k]:.4f} (esperado {REF[k]})")
    res["pr_auc"] = float(average_precision_score(y, ref))
    res["referencia_pr_auc"] = float(y.mean())
    if round(res["pr_auc"], 3) != REF["pr_auc"]:
        fallos.append(f"PR-AUC: {res['pr_auc']:.4f} (esperado {REF['pr_auc']})")
    # El clasificador del repositorio debe dar los mismos conteos que el cálculo directo
    pred_repo = modelo.clasificar(puntaje_b, metadatos=metadatos)
    res["clasificar_repo"] = (int((pred_repo & (y == 1)).sum()), int((pred_repo & (y == 0)).sum()))
    if res["clasificar_repo"] != (REF["detectadas"], REF["falsas_alarmas"]):
        fallos.append(f"clasificar() sobre (b): {res['clasificar_repo']}")

    # Importancias
    imp = modelo.importancias(pipeline, metadatos)
    res["importancias"] = imp
    for (var, val), (var_r, val_r) in zip(REF_TOP5, list(imp.items())[:5]):
        if (var, val) != (var_r, val_r):
            fallos.append(f"importancias: se esperaba {var} {val} y salió {var_r} {val_r}")
    if abs(imp["liquidez_corriente"] - 3.7) > 0.05:
        fallos.append(f"liquidez_corriente {imp['liquidez_corriente']} (esperada ≈ 3.7)")
    if guardar:
        carpeta = RAIZ / "reports"
        carpeta.mkdir(exist_ok=True)
        imp.rename_axis("variable").reset_index().to_csv(
            carpeta / "importancias_modelo.csv", index=False, encoding="utf-8")
    return res, fallos


def imprimir(res, fallos):
    print("=== Prueba de integridad ===")
    print(f"Observaciones: {res.get('n_observaciones')} | empresas: {res.get('n_empresas')}")
    for e, nombre in (("a", "(a) variables de dataset_prueba.csv"),
                      ("b", "(b) variables recalculadas con indicadores.py")):
        if e in res:
            print(f"{nombre}: diferencia máxima {res[e]['maxima']:.3e}; "
                  f"observaciones que difieren (> {TOLERANCIA}): {res[e]['n_difieren']}")
    if "b_filas_cruce" in res:
        print(f"(b) cruce por (empresa, anio): {res['b_filas_cruce']} filas; primeros años: "
              f"{res['b_primer_anio']}; ingresos_anio_anterior NaN: {res['b_nan_ingresos_prev']}")
    if "metricas" in res:
        print(f"Observaciones de riesgo: {res['positivos']}")
        for c, m in res["metricas"].items():
            print(f"  criterio '{c}': detectadas={m['detectadas']} falsas_alarmas={m['falsas_alarmas']} "
                  f"F1={m['f1']:.4f} recall={m['recall']:.4f} precisión={m['precision']:.4f}")
        print(f"Criterio usado por el repositorio: '{res['criterio_usado']}'; "
              f"clasificar() sobre (b): detectadas={res['clasificar_repo'][0]}, "
              f"falsas_alarmas={res['clasificar_repo'][1]}")
        print(f"PR-AUC: {res['pr_auc']:.4f} (referencia sin capacidad predictiva: {res['referencia_pr_auc']:.4f})")
    if "importancias" in res:
        print("Importancias (17 variables, %):")
        print(res["importancias"].to_string())
    print("RESULTADO:", "COINCIDE" if not fallos else "NO COINCIDE")
    for f in fallos:
        print(" -", f)


if __name__ == "__main__":
    faltan = [str(p.relative_to(RAIZ)) for p in archivos_requeridos() if not p.exists()]
    if faltan:
        print("Faltan archivos:", faltan)
        sys.exit(2)
    resultados, problemas = ejecutar()
    imprimir(resultados, problemas)
    sys.exit(1 if problemas else 0)
