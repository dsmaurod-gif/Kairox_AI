"""Elimina los metadatos de cuenta de Google de un cuaderno (.ipynb) y verifica el resultado.

Quita `metadata.executionInfo.user` de cada celda y comprueba que en TODO el archivo no
queden las claves `displayName` y `userId` ni direcciones de correo.

Uso:
  python scripts/limpiar_cuaderno.py ENTRADA.ipynb            # solo informa (no escribe)
  python scripts/limpiar_cuaderno.py ENTRADA.ipynb -o SALIDA.ipynb
  python scripts/limpiar_cuaderno.py ENTRADA.ipynb --in-place
Código de salida: 0 = limpio; 1 = quedan metadatos de cuenta (no se escribe nada); 2 = error de uso.
"""
import argparse
import json
import re
import sys
from pathlib import Path

CLAVES_PROHIBIDAS = {"displayName", "userId"}
CORREO = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def limpiar(cuaderno):
    """Quita executionInfo.user de cada celda. Devuelve cuántas se limpiaron."""
    n = 0
    for celda in cuaderno.get("cells", []):
        info = celda.get("metadata", {}).get("executionInfo")
        if isinstance(info, dict) and "user" in info:
            del info["user"]
            n += 1
    return n


def verificar(objeto, ruta="$"):
    """Lista de hallazgos (ruta, motivo): claves prohibidas y correos, en cualquier nivel."""
    hallazgos = []
    if isinstance(objeto, dict):
        for clave, valor in objeto.items():
            if clave in CLAVES_PROHIBIDAS:
                hallazgos.append((f"{ruta}.{clave}", f"clave «{clave}»"))
            hallazgos += verificar(valor, f"{ruta}.{clave}")
    elif isinstance(objeto, list):
        for i, valor in enumerate(objeto):
            hallazgos += verificar(valor, f"{ruta}[{i}]")
    elif isinstance(objeto, str):
        for correo in CORREO.findall(objeto):
            hallazgos.append((ruta, "correo electrónico"))
    return hallazgos


def principal(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    destino = ap.add_mutually_exclusive_group()
    destino.add_argument("-o", "--salida", help="ruta del cuaderno limpio")
    destino.add_argument("--in-place", action="store_true", help="sobrescribe la entrada")
    args = ap.parse_args(argv)
    ruta = Path(args.entrada)
    try:
        cuaderno = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"No se pudo leer el cuaderno: {error}")
        return 2
    antes = verificar(cuaderno)
    n = limpiar(cuaderno)
    despues = verificar(cuaderno)
    print(f"Celdas con executionInfo.user eliminado: {n}")
    print(f"Hallazgos antes de limpiar: {len(antes)}; después: {len(despues)}")
    for donde, motivo in despues:
        print(f"  QUEDA {motivo} en {donde}")
    if despues:
        print("RESULTADO: NO LIMPIO (no se escribió nada)")
        return 1
    print("RESULTADO: LIMPIO (sin displayName, userId ni correos)")
    destino_ruta = ruta if args.in_place else (Path(args.salida) if args.salida else None)
    if destino_ruta is None:
        print("Sin -o ni --in-place: no se escribió ningún archivo.")
        return 0
    destino_ruta.write_text(json.dumps(cuaderno, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Escrito: {destino_ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
