"""Pruebas de la app con streamlit.testing (sin navegador). No dependen de datos_locales/."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from kairox import ejemplos
from kairox.indicadores import CIFRAS_ENTRADA

RUTA_APP = str(Path(__file__).resolve().parents[1] / "app" / "app.py")


def _app():
    at = AppTest.from_file(RUTA_APP, default_timeout=60)
    at.run()
    assert not at.exception
    return at


def _html(at):
    return "\n".join(m.value for m in at.markdown)


def test_carga_sin_excepciones_y_sin_resultado():
    at = _app()
    html = _html(at)
    assert "Kairox AI" in html and "Para qué sirve y para qué no" in html
    assert "Puntaje de riesgo" not in html  # aún no se analizó
    assert at.button(key="analizar").disabled  # sin activo_total hay bloqueos
    assert "El activo total debe ser mayor que cero" in html


@pytest.mark.parametrize("caso,etiqueta,ocurrio", [
    (1, "Riesgo crítico", "la empresa quebró"),
    (2, "Riesgo crítico", "la empresa no quebró"),
    (3, "Inversión viable", "la empresa quebró"),
])
def test_ejemplos_un_clic(caso, etiqueta, ocurrio):
    at = _app()
    at.button(key=f"ej_{caso}").click().run()
    assert not at.exception
    fila = ejemplos.cargar_ejemplos().iloc[caso - 1]
    html = _html(at)
    assert f"{fila['puntaje_referencia']:.2f}" in html and etiqueta in html
    assert f"Lo que ocurrió: {ocurrio}" in html and ejemplos.rotulo(fila["tipo"]) in html
    assert "Umbral 0.50" in html and "Variables que más usa el modelo" in html
    assert "Tiempo de cálculo de la última predicción" in html
    # el puntaje no se presenta como probabilidad ni como porcentaje
    assert "robabilidad real" in html and "% de probabilidad" not in html
    assert f"{fila['puntaje_referencia'] * 100:.0f} %" not in html


def test_campos_manuales_parten_del_ejemplo_y_editar_oculta_rotulo():
    at = _app()
    at.button(key="ej_1").click().run()
    assert at.number_input(key="in_activo_total").value == pytest.approx(18047.101)
    assert "Lo que ocurrió" in _html(at)
    at.number_input(key="in_activo_total").set_value(18000.0).run()
    assert not at.exception
    html = _html(at)
    assert "Lo que ocurrió: la empresa" not in html and "modificadas" in html
    assert "Puntaje de riesgo" in html  # el resultado se recalcula


def test_bloqueo_desactiva_el_boton():
    at = _app()
    at.button(key="ej_1").click().run()
    assert not at.button(key="analizar").disabled
    at.number_input(key="in_activo_total").set_value(0.0).run()
    assert at.button(key="analizar").disabled
    assert "Puntaje de riesgo" not in _html(at)


def test_manual_analizar():
    at = _app()
    for clave in CIFRAS_ENTRADA:
        at.number_input(key=f"in_{clave}").set_value(100.0)
    at.run()
    assert not at.button(key="analizar").disabled
    at.button(key="analizar").click().run()
    assert not at.exception and "Puntaje de riesgo" in _html(at)
