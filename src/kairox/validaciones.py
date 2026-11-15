"""Validación de las 16 cifras de entrada y lectura del CSV de una empresa (RNF04).

Ninguna función lanza excepciones por entradas inválidas: devuelven mensajes.
Los límites de escala se leen de models/parametros_modelo.json.
"""
import csv
import io
import json
import math
from pathlib import Path

from kairox.indicadores import CIFRAS_ENTRADA

RAIZ = Path(__file__).resolve().parents[2]
with open(RAIZ / "models" / "parametros_modelo.json", encoding="utf-8") as _f:
    _EQUIV = json.load(_f)["activo_total_equivalente_millones"]
ACTIVO_P1, ACTIVO_P99 = _EQUIV["p1"], _EQUIV["p99"]
ACTIVO_MAXIMO_MILLONES = 1_000_000
MINIMO_CIFRAS = 9


def _como_numero(valor):
    """Devuelve (numero_o_None, es_invalido). None/vacío/NaN -> faltante sin error."""
    if valor is None or isinstance(valor, bool):
        return None, isinstance(valor, bool)
    if isinstance(valor, str):
        texto = valor.strip()
        if texto == "":
            return None, False
        try:
            valor = float(texto)
        except ValueError:
            return None, True
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None, True
    if math.isnan(numero):
        return None, False
    if math.isinf(numero):
        return None, True
    return numero, False


def normalizar_cifras(cifras):
    """(dict {cifra: float | None}, lista de cifras con valor no numérico)."""
    limpias, invalidas = {}, []
    origen = cifras if isinstance(cifras, dict) else {}
    for clave in CIFRAS_ENTRADA:
        numero, invalido = _como_numero(origen.get(clave))
        limpias[clave] = numero
        if invalido:
            invalidas.append(clave)
    return limpias, invalidas


def validar_cifras(cifras):
    """{'bloqueos': [...], 'avisos': [...]}; con bloqueos no debe analizarse."""
    bloqueos, avisos = [], []
    if not isinstance(cifras, dict):
        return {"bloqueos": ["No se recibieron cifras para analizar."], "avisos": []}
    c, invalidas = normalizar_cifras(cifras)
    for clave in invalidas:
        avisos.append(f"El valor de «{clave}» no es un número válido y se tratará como dato faltante.")
    presentes = sum(v is not None for v in c.values())
    faltan = len(CIFRAS_ENTRADA) - presentes

    activo = c["activo_total"]
    if activo is None or activo <= 0:
        bloqueos.append("El activo total debe ser mayor que cero: de él dependen casi todos los indicadores.")
    if presentes < MINIMO_CIFRAS:
        bloqueos.append("Con menos de 9 cifras el análisis no es confiable (criterio de diseño del sistema).")

    if faltan > 0:
        avisos.append(f"Faltan {faltan} de 16 cifras. Los indicadores que dependen de ellas se imputarán "
                      "con la mediana y el resultado será menos confiable.")
    if activo is not None and c["activo_corriente"] is not None and c["activo_corriente"] > activo:
        avisos.append("El activo corriente es mayor que el activo total: revise las cifras.")
    if c["pasivo_total"] is not None and c["pasivo_total"] < 0:
        avisos.append("El pasivo total es negativo: revise las cifras.")
    if c["ingresos_totales"] is None or c["ingresos_totales"] == 0:
        avisos.append("Los ingresos totales están ausentes o son cero: los indicadores que dependen "
                      "de ellos quedan sin dato.")
    if c["ingresos_anio_anterior"] is None:
        avisos.append("Falta el ingreso del año anterior: el crecimiento de ingresos queda sin dato.")
    if activo is not None and activo > 0:
        if activo < ACTIVO_P1 or activo > ACTIVO_P99:
            avisos.append("Fuera del rango de entrenamiento: el modelo recorta este valor.")
        if activo > ACTIVO_MAXIMO_MILLONES:
            avisos.append("Posible error de unidades: las cifras deben estar en millones de dólares.")
    return {"bloqueos": bloqueos, "avisos": avisos}


def _leer_texto(archivo):
    if isinstance(archivo, (str, Path)):
        crudo = Path(archivo).read_bytes()
    elif hasattr(archivo, "read"):
        crudo = archivo.read()
    else:
        raise TypeError("tipo de archivo no admitido")
    if isinstance(crudo, str):
        return crudo
    try:
        return crudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        return crudo.decode("latin-1")


def leer_csv(archivo):
    """Lee las cifras de la PRIMERA fila de un CSV. Devuelve (cifras, mensajes).

    Encabezados en minúscula; separador ',' o ';' (con ';' se acepta coma decimal).
    Nunca lanza excepciones: los problemas se devuelven como mensajes.
    """
    mensajes = []
    try:
        texto = _leer_texto(archivo)
        lineas = [l for l in texto.splitlines() if l.strip()]
        if len(lineas) < 2:
            return {}, ["El archivo está vacío o no contiene una fila de datos."]
        sep = ";" if lineas[0].count(";") > lineas[0].count(",") else ","
        filas = list(csv.reader(io.StringIO("\n".join(lineas)), delimiter=sep))
        encabezados = [h.strip().lower() for h in filas[0]]
        if len(filas) > 2:
            mensajes.append("El archivo tiene más de una fila de datos: solo se usa la primera.")
        cifras = {}
        for nombre, valor in zip(encabezados, filas[1]):
            if nombre not in CIFRAS_ENTRADA:
                continue
            texto_valor = valor.strip()
            if sep == ";":
                texto_valor = texto_valor.replace(",", ".")
            numero, invalido = _como_numero(texto_valor)
            if invalido:
                mensajes.append(f"El valor «{valor.strip()}» de la columna «{nombre}» no es numérico; "
                                "se tratará como dato faltante.")
            cifras[nombre] = numero
        ausentes = [c for c in CIFRAS_ENTRADA if c not in encabezados]
        if ausentes:
            mensajes.append("Faltan columnas en el archivo: " + ", ".join(ausentes) + ".")
        return cifras, mensajes
    except Exception:  # RNF04: nunca una excepción hacia la interfaz
        return {}, ["No se pudo leer el archivo: verifique que sea un CSV de texto con encabezados."]
