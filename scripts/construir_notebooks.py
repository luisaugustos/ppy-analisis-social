"""Construye los notebooks de cada sesión a partir de los textos de ``_fuente``.

Cada fichero ``_fuente/sNN_teoria.txt`` o ``_fuente/sNN_practica.txt`` se divide
en celdas con las marcas ``#%% md`` y ``#%% code``. En las prácticas, el código
situado entre ``#>>>`` y ``#<<<`` es la solución: aparece en
``practica_resuelta.ipynb`` y se sustituye por ``...`` en ``practica.ipynb``.
Así basta con editar un único fichero por práctica.

Tras el tipo de celda pueden ir etiquetas: ``solo-clase`` (la celda no pasa al
libro), ``solo-libro`` (no aparece en los notebooks de clase) o cualquier
etiqueta de Jupyter Book (``hide-cell``, ``remove-output``...). El libro se
genera con ``scripts/construir_libro.py``.

    uv run python scripts/construir_notebooks.py
"""
import re
from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "_fuente"
CARPETAS = {
    "s01": "s01_presentacion_y_repaso", "s02": "s02_programacion_cientifica",
    "s03": "s03_datos_tabulares_1", "s04": "s04_datos_tabulares_2",
    "s05": "s05_visualizacion", "s06": "s06_analisis_exploratorio",
}

ARRANQUE = """# Preparacion: localiza la carpeta de la asignatura (y la descarga si estas en Google Colab).
# Ejecuta esta celda primero; no hace falta entenderla todavia.
import os, subprocess
from pathlib import Path

REPO = "https://github.com/luisaugustos/ppy-analisis-social.git"


def _buscar_carpeta():
    for carpeta in [Path.cwd(), *Path.cwd().parents]:
        for candidata in (carpeta, carpeta / "ppy-analisis-social"):
            if (candidata / "datos" / "ORIGEN.md").is_file():
                return candidata
    return None


raiz = _buscar_carpeta()
if raiz is None:
    subprocess.run(["git", "clone", "--depth", "1", REPO], check=True)
    raiz = Path("ppy-analisis-social").resolve()

os.chdir(raiz)
print("Carpeta de trabajo lista. Los datos estan en la subcarpeta 'datos'.")"""


def bloques(texto: str):
    """Devuelve (tipo, etiquetas, cuerpo) de cada celda del texto fuente."""
    for bloque in re.split(r"^#%% ", texto, flags=re.M)[1:]:
        cabecera, _, cuerpo = bloque.partition("\n")
        tipo, *etiquetas = cabecera.split()
        yield tipo, etiquetas, cuerpo.strip("\n")


def resolver(cuerpo: str, resuelta: bool) -> str:
    if resuelta:
        return re.sub(r"^[ \t]*#(>>>|<<<)[ \t]*\n?", "", cuerpo, flags=re.M).rstrip()
    return re.sub(r"^([ \t]*)#>>>.*?#<<<[ \t]*$", r"\1...", cuerpo, flags=re.M | re.S).rstrip()


def sin_directivas(cuerpo: str) -> str:
    """Jupyter y Colab no entienden las cajas de MyST: se convierten en citas."""
    def cita(m):
        lineas = [l for l in m.group(2).strip().splitlines() if not l.startswith(":class:")]
        texto = "\n".join("> " + l if l.strip() else ">" for l in lineas).strip("\n>")
        return f"> **{m.group(1).strip()}**\n>\n{texto if texto.startswith('>') else '> ' + texto}"
    return re.sub(r"^```\{admonition\} (.+?)\n(.*?)^```[ \t]*$", cita, cuerpo, flags=re.M | re.S)


def celdas(texto: str, resuelta: bool):
    """Celdas para clase: se omiten las marcadas como ``solo-libro``."""
    out = []
    for tipo, etiquetas, cuerpo in bloques(texto):
        if "solo-libro" in etiquetas:
            continue
        if tipo == "md":
            out.append(nbf.v4.new_markdown_cell(sin_directivas(cuerpo)))
        else:
            out.append(nbf.v4.new_code_cell(resolver(cuerpo, resuelta)))
    return out


def construir(origen: Path, destino: Path, resuelta: bool):
    nb = nbf.v4.new_notebook()
    cs = celdas(origen.read_text(encoding="utf-8"), resuelta)
    nb.cells = [cs[0], nbf.v4.new_code_cell(ARRANQUE), *cs[1:]]
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    destino.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, destino)
    print("  ", destino.relative_to(RAIZ))


if __name__ == "__main__":
    for f in sorted(FUENTE.glob("s*_*.txt")):
        ses, tipo = f.stem.split("_", 1)
        carpeta = RAIZ / "sesiones" / CARPETAS[ses]
        if tipo == "teoria":
            construir(f, carpeta / f"{ses}_teoria.ipynb", resuelta=True)
        else:
            construir(f, carpeta / f"{ses}_practica.ipynb", resuelta=False)
            construir(f, carpeta / f"{ses}_practica_resuelta.ipynb", resuelta=True)
