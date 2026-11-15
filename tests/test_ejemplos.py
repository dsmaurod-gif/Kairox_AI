"""Casos de ejemplo y plantilla. Las pruebas principales corren SIN los datasets:
el puntaje recalculado a partir de las 16 cifras debe igualar `puntaje_referencia`."""
import io
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kairox import ejemplos, modelo
from kairox.indicadores import CIFRAS_ENTRADA, calcular_variables
from kairox.validaciones import ACTIVO_P1, ACTIVO_P99, leer_csv, validar_cifras

RAIZ = Path(__file__).resolve().parents[1]
COLUMNAS = ["caso", "tipo", "empresa", "anio"] + CIFRAS_ENTRADA + ["riesgo_real", "puntaje_referencia"]


@pytest.fixture(scope="module")
def mod():
    return modelo.cargar_modelo()


@pytest.fixture(scope="module")
def casos():
    return ejemplos.cargar_ejemplos()


def test_estructura(casos):
    assert list(casos.columns) == COLUMNAS and len(casos) == 3
    assert casos["tipo"].tolist() == ["acierto", "falsa alarma", "caso no detectado"]
    assert pd.api.types.is_integer_dtype(casos["anio"])
    assert not casos[CIFRAS_ENTRADA].isna().any().any()  # las 16 cifras completas


def test_puntaje_recalculado_igual_a_referencia(casos, mod):
    pipe, meta, _ = mod
    for _, fila in casos.iterrows():
        v = calcular_variables(ejemplos.cifras_de(fila))
        puntaje = modelo.puntuar(v, pipe, meta)[0]
        assert abs(puntaje - fila["puntaje_referencia"]) <= 1e-9, fila["tipo"]


def test_tipo_coherente_con_umbral_y_riesgo_real(casos, mod):
    umbral = mod[1]["umbral_decision"]
    esperado = {"acierto": (1, True), "falsa alarma": (0, True), "caso no detectado": (1, False)}
    for _, fila in casos.iterrows():
        real, alto = esperado[fila["tipo"]]
        assert fila["riesgo_real"] == real
        assert bool(modelo.clasificar(fila["puntaje_referencia"], umbral)) == alto


def test_activo_total_dentro_de_rango_y_sin_bloqueos(casos):
    for _, fila in casos.iterrows():
        assert ACTIVO_P1 <= fila["activo_total"] <= ACTIVO_P99
        r = validar_cifras(ejemplos.cifras_de(fila))
        assert r["bloqueos"] == [] and not any("Faltan" in a for a in r["avisos"])


def test_textos_de_interfaz(casos):
    assert ejemplos.rotulo("acierto") == ("Caso elegido para mostrar un acierto; "
                                          "no representa el desempeño general.")
    assert "una falsa alarma" in ejemplos.rotulo("falsa alarma")
    assert "un caso no detectado" in ejemplos.rotulo("caso no detectado")
    assert ejemplos.lo_que_ocurrio(1) == "Lo que ocurrió: la empresa quebró"
    assert ejemplos.lo_que_ocurrio(0) == "Lo que ocurrió: la empresa no quebró"


def test_plantilla():
    df = pd.read_csv(ejemplos.RUTA_PLANTILLA)
    assert list(df.columns) == CIFRAS_ENTRADA and len(df) == 1
    cifras, mensajes = leer_csv(io.BytesIO(ejemplos.contenido_plantilla()))
    assert mensajes == [] and len(cifras) == 16
    r = validar_cifras(cifras)
    assert r["bloqueos"] == [] and r["avisos"] == []


def test_casos_coinciden_con_el_conjunto_de_prueba(casos):
    """Verificación contra los datos originales (requiere datos_locales/)."""
    ruta_p, ruta_n = RAIZ / "datos_locales" / "dataset_prueba.csv", RAIZ / "datos_locales" / "proba_prueba.npy"
    for ruta in (ruta_p, ruta_n):
        if not ruta.exists():
            pytest.skip(f"requiere datos_locales/{ruta.name}")
    prueba = pd.read_csv(ruta_p)
    prueba["puntaje"] = np.load(ruta_n)
    for _, fila in casos.iterrows():
        sel = prueba[(prueba["empresa"] == fila["empresa"]) & (prueba["anio"] == fila["anio"])]
        assert len(sel) == 1, f"{fila['empresa']} {fila['anio']} no está en el conjunto de prueba"
        assert sel["puntaje"].iloc[0] == fila["puntaje_referencia"]
        assert int(sel["riesgo_critico"].iloc[0]) == fila["riesgo_real"]
