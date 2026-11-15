"""Integridad: la app usa el mismo modelo que se evaluó (ver scripts/verificar_integridad.py)."""
import importlib.util
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]  # independiente del directorio actual


def _script():
    spec = importlib.util.spec_from_file_location(
        "verificar_integridad", RAIZ / "scripts" / "verificar_integridad.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def resultado():
    s = _script()
    for ruta in s.archivos_requeridos():
        if not ruta.exists():
            pytest.skip(f"requiere datos_locales/{ruta.name}")
    return s.ejecutar(guardar=False)


def test_integridad_completa(resultado):
    res, fallos = resultado
    assert not fallos, "\n".join(fallos)


def test_diferencia_maxima_a_y_b(resultado):
    res, _ = resultado
    assert res["a"]["maxima"] <= 1e-9 and res["a"]["n_difieren"] == 0
    assert res["b"]["maxima"] <= 1e-9 and res["b"]["n_difieren"] == 0
    assert res["b_filas_cruce"] == 15742


def test_conteos_y_criterio(resultado):
    res, _ = resultado
    m = res["metricas"][res["criterio_usado"]]
    assert (m["detectadas"], m["falsas_alarmas"]) == (407, 2516)
    assert res["clasificar_repo"] == (407, 2516)


def test_importancias(resultado):
    res, _ = resultado
    imp = res["importancias"]
    assert len(imp) == 17
    assert list(imp.items())[:5] == [("deuda_lp_activos", 10.5), ("tamano_empresa", 8.8),
                                     ("valor_mercado_pasivos", 7.3), ("margen_bruto", 7.1),
                                     ("margen_neto", 6.5)]
