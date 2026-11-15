"""RNF03: tiempo de cálculo de 100 llamadas de puntuar + explicacion (límite: 5 s)."""
import statistics
import time

from kairox import modelo
from kairox.explicacion import explicar
from kairox.indicadores import calcular_variables

BASE = dict(
    activo_corriente=50.0, pasivo_corriente=25.0, inventario=10.0, activo_total=200.0,
    pasivo_total=100.0, deuda_largo_plazo=40.0, utilidades_retenidas=30.0,
    cuentas_por_cobrar=20.0, valor_mercado=300.0, ingresos_totales=150.0,
    ingresos_anio_anterior=100.0, utilidad_bruta=60.0, ebitda=30.0, ebit=20.0,
    utilidad_neta=12.0, gastos_operativos=130.0,
)
LIMITE_SEGUNDOS = 5.0


def test_rendimiento_100_llamadas():
    pipe, meta, par = modelo.cargar_modelo()
    modelo.puntuar(calcular_variables(BASE), pipe, meta)  # calentamiento (no se mide)
    tiempos = []
    for _ in range(100):
        t0 = time.perf_counter()
        v = calcular_variables(BASE)
        modelo.puntuar(v, pipe, meta)
        explicar(v, pipe, meta, par)
        tiempos.append(time.perf_counter() - t0)
    mediana, maximo = statistics.median(tiempos), max(tiempos)
    print(f"\nRNF03 (100 llamadas de puntuar + explicacion): mediana {mediana:.4f} s; "
          f"máximo {maximo:.4f} s; límite {LIMITE_SEGUNDOS} s")
    assert maximo < LIMITE_SEGUNDOS
