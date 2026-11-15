"""RNF04 (entradas inválidas dan mensajes, no excepciones; resultado determinista),
validaciones.py y explicacion.py. No dependen de datos_locales/."""
import io

import numpy as np
import pytest

from kairox import modelo
from kairox.explicacion import NOTA_APROXIMACION, explicar
from kairox.indicadores import CIFRAS_ENTRADA, calcular_variables
from kairox.validaciones import ACTIVO_P1, ACTIVO_P99, leer_csv, validar_cifras

BASE = dict(
    activo_corriente=50.0, pasivo_corriente=25.0, inventario=10.0, activo_total=200.0,
    pasivo_total=100.0, deuda_largo_plazo=40.0, utilidades_retenidas=30.0,
    cuentas_por_cobrar=20.0, valor_mercado=300.0, ingresos_totales=150.0,
    ingresos_anio_anterior=100.0, utilidad_bruta=60.0, ebitda=30.0, ebit=20.0,
    utilidad_neta=12.0, gastos_operativos=130.0,
)
ENCABEZADO = ",".join(CIFRAS_ENTRADA)


@pytest.fixture(scope="module")
def mod():
    return modelo.cargar_modelo()


def _val(**cambios):
    return validar_cifras({**BASE, **cambios})


# --- bloqueos ---
def test_cifras_completas_sin_bloqueos_ni_avisos():
    assert _val() == {"bloqueos": [], "avisos": []}


@pytest.mark.parametrize("valor", [None, 0, -5, np.nan, "abc"])
def test_bloqueo_activo_total(valor):
    r = _val(activo_total=valor)
    assert ("El activo total debe ser mayor que cero: de él dependen casi todos los "
            "indicadores.") in r["bloqueos"]


def test_bloqueo_menos_de_9_cifras():
    r = validar_cifras({k: BASE[k] for k in CIFRAS_ENTRADA[:8]} | {"activo_total": 200.0})
    assert ("Con menos de 9 cifras el análisis no es confiable (criterio de diseño del "
            "sistema).") in r["bloqueos"]
    # exactamente 9 cifras no bloquea por este motivo
    nueve = {k: BASE[k] for k in CIFRAS_ENTRADA[:8]} | {"activo_total": 200.0, "ebit": 1.0}
    assert len([k for k, v in nueve.items() if v is not None]) >= 9
    assert not any("menos de 9" in b for b in validar_cifras(nueve)["bloqueos"])


def test_cero_cuenta_como_cifra_presente():
    cifras = {k: 0.0 for k in CIFRAS_ENTRADA[:9]} | {"activo_total": 5.0}
    assert not any("menos de 9" in b for b in validar_cifras(cifras)["bloqueos"])


# --- avisos ---
def test_aviso_faltan_cifras():
    r = _val(inventario=None, ebit=None)
    assert ("Faltan 2 de 16 cifras. Los indicadores que dependen de ellas se imputarán con la "
            "mediana y el resultado será menos confiable.") in r["avisos"]


def test_avisos_coherencia():
    assert any("activo corriente es mayor" in a for a in _val(activo_corriente=500.0)["avisos"])
    assert any("pasivo total es negativo" in a for a in _val(pasivo_total=-1.0)["avisos"])
    assert any("ingresos totales" in a for a in _val(ingresos_totales=0)["avisos"])
    assert any("ingresos totales" in a for a in _val(ingresos_totales=None)["avisos"])
    assert any("año anterior" in a and "crecimiento de ingresos queda sin dato" in a
               for a in _val(ingresos_anio_anterior=None)["avisos"])


def test_avisos_de_escala():
    fuera = "Fuera del rango de entrenamiento: el modelo recorta este valor"
    assert any(fuera in a for a in _val(activo_total=ACTIVO_P1 / 10)["avisos"])
    assert any(fuera in a for a in _val(activo_total=ACTIVO_P99 * 2)["avisos"])
    assert not any(fuera in a for a in _val(activo_total=ACTIVO_P1 * 2)["avisos"])
    unidades = "Posible error de unidades: las cifras deben estar en millones de dólares"
    r = _val(activo_total=5_000_000.0)
    assert any(unidades in a for a in r["avisos"]) and r["bloqueos"] == []
    assert not any(unidades in a for a in _val(activo_total=ACTIVO_P99 * 2)["avisos"])


# --- RNF04: entradas inválidas dan mensajes, no excepciones ---
@pytest.mark.parametrize("entrada", [None, [], "texto", 5, {}, {"activo_total": "x"},
                                     {"activo_total": float("inf")}, {"zzz": 1},
                                     {k: "abc" for k in CIFRAS_ENTRADA},
                                     {k: None for k in CIFRAS_ENTRADA}, {"activo_total": True}])
def test_entradas_invalidas_no_lanzan(entrada):
    r = validar_cifras(entrada)
    assert set(r) == {"bloqueos", "avisos"} and len(r["bloqueos"]) >= 1


@pytest.mark.parametrize("contenido", [b"", b"\xff\xfe\x00", b"a,b\n", b"\x00\x01\x02", "ñ;ñ\n1;2",
                                       b"activo_total\nabc", None, 12345])
def test_csv_invalido_no_lanza(contenido):
    cifras, mensajes = leer_csv(io.BytesIO(contenido) if isinstance(contenido, bytes)
                                else io.StringIO(contenido) if isinstance(contenido, str) else contenido)
    assert isinstance(cifras, dict) and isinstance(mensajes, list)


def test_csv_coma_y_primera_fila(tmp_path):
    fila = ",".join(str(BASE[k]) for k in CIFRAS_ENTRADA)
    ruta = tmp_path / "e.csv"
    ruta.write_text(f"{ENCABEZADO.upper()}\n{fila}\n{fila}\n", encoding="utf-8")
    cifras, mensajes = leer_csv(ruta)
    assert cifras["activo_total"] == 200.0 and len(cifras) == 16
    assert any("más de una fila" in m for m in mensajes)


def test_csv_punto_y_coma_con_coma_decimal():
    fila = ";".join(str(BASE[k]).replace(".", ",") for k in CIFRAS_ENTRADA)
    cifras, mensajes = leer_csv(io.BytesIO(f"{ENCABEZADO.replace(',', ';')}\n{fila}".encode()))
    assert cifras["liquidez" if False else "activo_corriente"] == 50.0
    assert cifras["utilidad_neta"] == 12.0 and mensajes == []


def test_csv_valor_no_numerico_y_columnas_faltantes():
    cifras, mensajes = leer_csv(io.StringIO("activo_total,ebit\n12abc,5"))
    assert cifras["activo_total"] is None and cifras["ebit"] == 5.0
    assert any("no es numérico" in m for m in mensajes)
    assert any(m.startswith("Faltan columnas") for m in mensajes)


# --- determinismo (RNF04) ---
def test_mismo_dato_mismo_puntaje_100_llamadas(mod):
    pipe, meta, _ = mod
    v = calcular_variables(BASE)
    puntajes = [float(modelo.puntuar(v, pipe, meta)[0]) for _ in range(100)]
    assert len(set(puntajes)) == 1  # exactamente igual, sin tolerancia
    x = [explicar(v, pipe, meta, mod[2])["puntaje"] for _ in range(100)]
    assert len(set(x)) == 1


# --- explicacion.py ---
class _Espia:
    def __init__(self, pipe):
        self._pipe, self.llamadas = pipe, 0

    def predict_proba(self, X):
        self.llamadas += 1
        return self._pipe.predict_proba(X)


def test_explicacion_un_solo_predict_proba(mod):
    pipe, meta, par = mod
    espia = _Espia(pipe)
    r = explicar(calcular_variables(BASE), espia, meta, par)
    assert espia.llamadas == 1
    assert len(r["efectos"]) == 5 and r["nota"] == NOTA_APROXIMACION
    absolutos = [abs(e["efecto"]) for e in r["efectos"]]
    assert absolutos == sorted(absolutos, reverse=True)
    s0 = modelo.puntuar(calcular_variables(BASE), pipe, meta)[0]
    assert r["puntaje"] == pytest.approx(s0, abs=1e-12)
    for e in r["efectos"]:
        assert (e["efecto"] > 0) == (e["direccion"] == "sube el puntaje") or e["efecto"] == 0


def test_explicacion_variable_sin_dato_efecto_cero(mod):
    pipe, meta, par = mod
    sin_datos = {k: BASE[k] for k in ("activo_total", "pasivo_total", "ebit", "utilidad_neta",
                                      "ingresos_totales", "activo_corriente", "pasivo_corriente",
                                      "valor_mercado", "utilidad_bruta")}
    v = calcular_variables(sin_datos)
    r = explicar(v, pipe, meta, par, n=17)
    por_var = {e["variable"]: e for e in r["efectos"]}
    assert por_var["crecimiento_ingresos"]["sin_dato"] and por_var["crecimiento_ingresos"]["efecto"] == 0
    assert por_var["crecimiento_ingresos"]["direccion"] == "sin dato"
    assert por_var["crecimiento_ingresos"]["valor"] is None
    assert por_var["deuda_lp_activos"]["sin_dato"]
