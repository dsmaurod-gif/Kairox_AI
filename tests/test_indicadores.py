"""Pruebas de indicadores.py: casos borde y verificación contra el entrenamiento."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kairox.indicadores import CIFRAS_ENTRADA, VARIABLES_MODELO, calcular_variables

RAIZ = Path(__file__).resolve().parents[1]  # independiente del directorio actual
DATOS = RAIZ / "datos_locales"

BASE = dict(
    activo_corriente=50.0, pasivo_corriente=25.0, inventario=10.0, activo_total=200.0,
    pasivo_total=100.0, deuda_largo_plazo=40.0, utilidades_retenidas=30.0,
    cuentas_por_cobrar=20.0, valor_mercado=300.0, ingresos_totales=150.0,
    ingresos_anio_anterior=100.0, utilidad_bruta=60.0, ebitda=30.0, ebit=20.0,
    utilidad_neta=12.0, gastos_operativos=130.0,
)


def _una(**cambios):
    return calcular_variables({**BASE, **cambios}).iloc[0]


def test_columnas_y_orden():
    r = calcular_variables(BASE)
    assert list(r.columns) == VARIABLES_MODELO and len(VARIABLES_MODELO) == 17
    assert len(CIFRAS_ENTRADA) == 16 and r.shape == (1, 17)


def test_valores_conocidos():
    r = _una()
    assert r.liquidez_corriente == pytest.approx(2.0)
    assert r.prueba_acida == pytest.approx(1.6)
    assert r.crecimiento_ingresos == pytest.approx(0.5)
    assert r.tamano_empresa == pytest.approx(np.log1p(200.0))


def test_denominador_cero_da_nan_no_infinito():
    r = _una(pasivo_corriente=0, activo_total=0, ingresos_totales=0, cuentas_por_cobrar=0,
             pasivo_total=0, ingresos_anio_anterior=0)
    for col in ["liquidez_corriente", "prueba_acida", "capital_trabajo_activos", "endeudamiento",
                "roa", "margen_neto", "valor_mercado_pasivos", "rotacion_activos",
                "rotacion_cuentas_cobrar", "crecimiento_ingresos"]:
        assert np.isnan(r[col]), col
    assert not np.isinf(r.to_numpy(dtype=float)).any()


def test_primer_anio_crecimiento_nan():
    assert np.isnan(_una(ingresos_anio_anterior=np.nan).crecimiento_ingresos)
    sin_columna = {k: v for k, v in BASE.items() if k != "ingresos_anio_anterior"}
    assert np.isnan(calcular_variables(sin_columna).iloc[0].crecimiento_ingresos)


def test_activo_total_no_positivo():
    # activo_total = 0 -> ratios NaN; tamano_empresa = log1p(0) = 0
    r0 = _una(activo_total=0)
    assert np.isnan(r0.endeudamiento) and r0.tamano_empresa == 0
    # activo_total < 0: no es NaN (solo el denominador 0 lo es); tamano_empresa = 0.
    # El bloqueo de activo_total <= 0 corresponde a validaciones.py.
    rn = _una(activo_total=-50)
    assert rn.tamano_empresa == 0 and rn.endeudamiento == pytest.approx(-2.0)


def test_nan_de_entrada_da_nan_de_salida():
    r = _una(activo_corriente=np.nan, activo_total=np.nan)
    assert np.isnan(r.liquidez_corriente) and np.isnan(r.prueba_acida)
    assert np.isnan(r.tamano_empresa) and np.isnan(r.endeudamiento)
    assert not np.isnan(r.margen_bruto)


def test_cifra_ausente_y_none_se_tratan_como_nan():
    r = calcular_variables({"activo_total": 100.0, "inventario": None}).iloc[0]
    assert np.isnan(r.liquidez_corriente) and np.isnan(r.prueba_acida)
    assert r.tamano_empresa == pytest.approx(np.log1p(100.0))


def test_varias_filas():
    df = pd.DataFrame([BASE, {**BASE, "activo_total": 400.0}])
    r = calcular_variables(df)
    assert r.shape == (2, 17) and r.endeudamiento.tolist() == pytest.approx([0.5, 0.25])


def test_contra_entrenamiento():
    """Variables recalculadas desde dataset_elaborado vs dataset_filtrado (<= 1e-9, mismos NaN)."""
    elab, filt = DATOS / "dataset_elaborado.csv", DATOS / "dataset_filtrado.csv"
    for ruta in (elab, filt):
        if not ruta.exists():
            pytest.skip(f"requiere datos_locales/{ruta.name}")
    e = pd.read_csv(elab).sort_values(["empresa", "anio"], kind="stable")
    e["ingresos_anio_anterior"] = e.groupby("empresa")["ingresos_totales"].shift(1)
    calc = calcular_variables(e[CIFRAS_ENTRADA])
    calc[["empresa", "anio"]] = e[["empresa", "anio"]]
    f = pd.read_csv(filt)
    m = f.merge(calc, on=["empresa", "anio"], suffixes=("_ref", "_calc"), validate="one_to_one")
    assert len(m) == len(f) == 78682
    maximos = {}
    for col in VARIABLES_MODELO:
        a, b = m[f"{col}_ref"].to_numpy(float), m[f"{col}_calc"].to_numpy(float)
        assert (np.isnan(a) == np.isnan(b)).all(), f"NaN distintos en {col}"
        ok = ~np.isnan(a)
        maximos[col] = float(np.max(np.abs(a[ok] - b[ok]))) if ok.any() else 0.0
    print("\nDiferencia máxima por variable:", maximos)
    assert max(maximos.values()) <= 1e-9, maximos
