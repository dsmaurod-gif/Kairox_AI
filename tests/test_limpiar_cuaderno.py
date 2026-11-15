"""Pruebas de scripts/limpiar_cuaderno.py con cuadernos sintéticos (datos ficticios)."""
import importlib.util
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("limpiar_cuaderno", RAIZ / "scripts" / "limpiar_cuaderno.py")
lc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lc)


def _cuaderno(extra_salida=None):
    celda = {"cell_type": "code", "source": ["1+1"], "outputs": extra_salida or [],
             "metadata": {"executionInfo": {"status": "ok", "user_tz": 300, "elapsed": 5,
                          "user": {"displayName": "Persona Ficticia", "userId": "123456789"}}}}
    return {"cells": [celda, dict(celda)], "metadata": {"colab": {"name": "x"}}, "nbformat": 4}


def _escribir(tmp_path, nb):
    ruta = tmp_path / "in.ipynb"
    ruta.write_text(json.dumps(nb), encoding="utf-8")
    return ruta


def test_detecta_y_limpia(tmp_path):
    nb = _cuaderno()
    nb["cells"][1] = json.loads(json.dumps(nb["cells"][1]))  # copia independiente
    assert len(lc.verificar(nb)) == 4  # 2 celdas x (displayName + userId)
    assert lc.limpiar(nb) == 2
    assert lc.verificar(nb) == []
    assert nb["cells"][0]["metadata"]["executionInfo"]["user_tz"] == 300  # lo demás se conserva


def test_salida_limpia_y_original_intacto(tmp_path):
    ruta = _escribir(tmp_path, _cuaderno())
    original = ruta.read_text(encoding="utf-8")
    assert lc.principal([str(ruta), "-o", str(tmp_path / "out.ipynb")]) == 0
    assert ruta.read_text(encoding="utf-8") == original  # sin --in-place no se toca
    limpio = (tmp_path / "out.ipynb").read_text(encoding="utf-8")
    assert "displayName" not in limpio and "userId" not in limpio


def test_sin_destino_no_escribe(tmp_path):
    ruta = _escribir(tmp_path, _cuaderno())
    assert lc.principal([str(ruta)]) == 0
    assert list(tmp_path.iterdir()) == [ruta]


def test_in_place(tmp_path):
    ruta = _escribir(tmp_path, _cuaderno())
    assert lc.principal([str(ruta), "--in-place"]) == 0
    assert "displayName" not in ruta.read_text(encoding="utf-8")


def test_queda_correo_falla_y_no_escribe(tmp_path):
    salida = [{"output_type": "stream", "text": ["contacto: persona@ejemplo.com"]}]
    ruta = _escribir(tmp_path, _cuaderno(salida))
    assert lc.principal([str(ruta), "-o", str(tmp_path / "out.ipynb")]) == 1
    assert not (tmp_path / "out.ipynb").exists()


def test_queda_clave_en_otro_nivel_falla(tmp_path):
    nb = _cuaderno()
    nb["metadata"]["colab"]["provenance"] = [{"userId": "999"}]
    ruta = _escribir(tmp_path, nb)
    assert lc.principal([str(ruta), "-o", str(tmp_path / "out.ipynb")]) == 1


def test_archivo_invalido_no_lanza(tmp_path):
    ruta = tmp_path / "malo.ipynb"
    ruta.write_text("no es json", encoding="utf-8")
    assert lc.principal([str(ruta)]) == 2
    assert lc.principal([str(tmp_path / "no_existe.ipynb")]) == 2
