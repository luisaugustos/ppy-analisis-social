"""Ejecuta de principio a fin los notebooks de teoría y las prácticas resueltas.

    uv run python scripts/probar_notebooks.py [s01 s02 ...]
"""
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

RAIZ = Path(__file__).resolve().parent.parent
filtros = sys.argv[1:]
fallos = 0
for ruta in sorted((RAIZ / "sesiones").rglob("*.ipynb")):
    if ruta.name.endswith("_practica.ipynb") or (filtros and not any(f in ruta.name for f in filtros)):
        continue
    nb = nbformat.read(ruta, as_version=4)
    try:
        NotebookClient(nb, timeout=300, kernel_name="python3",
                       resources={"metadata": {"path": str(ruta.parent)}}).execute()
        print("OK   ", ruta.relative_to(RAIZ))
    except Exception as e:  # noqa: BLE001
        fallos += 1
        print("FALLO", ruta.relative_to(RAIZ), "\n", str(e)[-1500:])
sys.exit(1 if fallos else 0)
