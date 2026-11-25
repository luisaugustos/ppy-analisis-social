"""Genera los capítulos del libro (TeachBook) a partir de los textos de ``_fuente``.

Cada sesión produce dos notebooks en la carpeta del libro:

- ``tN_<tema>.ipynb``: el capítulo, a partir de ``sNN_teoria.txt``.
- ``tN_ejercicios.ipynb``: la hoja de ejercicios, a partir de ``sNN_practica.txt``
  (sin soluciones).

Uso, desde la raíz de este repositorio:

    uv run python scripts/construir_libro.py              # genera los notebooks
    uv run python scripts/construir_libro.py --ejecutar   # además ejecuta los capítulos y guarda los resultados

Con ``--ejecutar`` los capítulos se ejecutan con los ficheros de ``datos/``.
Conviene lanzar antes ``scripts/descargar_datos.py``: el script avisa de los
ficheros que siguen siendo simulados.
"""
import argparse
import re
import sys
from pathlib import Path

import nbformat as nbf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from construir_notebooks import ARRANQUE, FUENTE, RAIZ, bloques, resolver  # noqa: E402

DESTINO = RAIZ.parent / "teachbook_python" / "book" / "es" / "02_analisis"
TEMAS = {
    "s01": "t1_presentacion", "s02": "t2_programacion_cientifica", "s03": "t3_datos_tabulares_1",
    "s04": "t4_datos_tabulares_2", "s05": "t5_visualizacion", "s06": "t6_analisis_exploratorio",
}
CIERRES = r"^## (\d+\. )?(Para cerrar|Para la próxima sesión)\b.*"


def adaptar_markdown(cuerpo: str, primera: bool, ejercicios: bool) -> str:
    """Quita lo que solo tiene sentido en clase (fechas, numeración, cierres)."""
    cuerpo = re.sub(CIERRES, "", cuerpo, flags=re.M | re.S).rstrip()
    cuerpo = re.sub(r"^(#{2,4}) \d+(\.\d+)*\.? +", r"\1 ", cuerpo, flags=re.M)
    cuerpo = re.sub(r"^## Parte ([AB]) · ", r"## ", cuerpo, flags=re.M)
    cuerpo = cuerpo.replace("Esta práctica la hacemos juntos, paso a paso: el profesor escribe y explica cada celda, y tú la reproduces en tu notebook.\n\n", "")
    if primera:
        cuerpo = re.sub(r"^# Sesión \d+ · (Práctica guiada: )?", "# Ejercicios: " if ejercicios else "# ", cuerpo)
        cuerpo = re.sub(r"^\*\*Programación avanzada en Python aplicada al análisis social\*\*.*\n+", "", cuerpo, flags=re.M)
        if ejercicios:
            titulo, _, resto = cuerpo.partition("\n")
            titulo = titulo[:14] + titulo[14].lower() + titulo[15:] if len(titulo) > 15 else titulo
            cuerpo = titulo + "\n" + resto
    return cuerpo


def construir(origen: Path, destino: Path, ejercicios: bool) -> None:
    celdas = []
    for tipo, etiquetas, cuerpo in bloques(origen.read_text(encoding="utf-8")):
        if "solo-clase" in etiquetas:
            continue
        etiquetas = [e for e in etiquetas if e != "solo-libro"]
        if tipo == "md":
            cuerpo = adaptar_markdown(cuerpo, primera=not celdas, ejercicios=ejercicios)
            if not cuerpo:
                continue
            celda = nbf.v4.new_markdown_cell(cuerpo)
        else:
            celda = nbf.v4.new_code_cell(resolver(cuerpo, resuelta=not ejercicios))
        if etiquetas:
            celda.metadata["tags"] = etiquetas
        celdas.append(celda)
    arranque = nbf.v4.new_code_cell(ARRANQUE)
    arranque.metadata["tags"] = ["hide-cell"]
    nb = nbf.v4.new_notebook()
    nb.cells = [celdas[0], arranque, *celdas[1:]]
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    destino.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, destino)
    print("  ", destino.name)


def ejecutar(ruta: Path) -> None:
    """Ejecuta un capítulo y guarda los resultados en el propio notebook."""
    import os

    from nbclient import NotebookClient

    # Los gráficos de Plotly se guardan como HTML para que el libro pueda mostrarlos.
    os.environ["PLOTLY_RENDERER"] = "notebook_connected"
    nb = nbf.read(ruta, as_version=4)
    NotebookClient(nb, timeout=600, kernel_name="python3", allow_errors=False,
                   resources={"metadata": {"path": str(RAIZ)}}).execute()
    nbf.write(nb, ruta)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--destino", type=Path, default=DESTINO, help="Carpeta del libro para estos capítulos")
    parser.add_argument("--ejecutar", action="store_true", help="Ejecutar los capítulos y guardar los resultados")
    args = parser.parse_args()

    print("Capítulos generados en", args.destino)
    capitulos = []
    for ses, tema in TEMAS.items():
        capitulo = args.destino / f"{tema}.ipynb"
        construir(FUENTE / f"{ses}_teoria.txt", capitulo, ejercicios=False)
        construir(FUENTE / f"{ses}_practica.txt", args.destino / f"{tema.split('_')[0]}_ejercicios.ipynb", ejercicios=True)
        capitulos.append(capitulo)

    if args.ejecutar:
        print("\nEjecutando capítulos (puede tardar unos minutos)...")
        for capitulo in capitulos:
            ejecutar(capitulo)
            print("   ejecutado:", capitulo.name)
        simulados = [l.split("|")[1].strip() for l in (RAIZ / "datos" / "ORIGEN.md").read_text(encoding="utf-8").splitlines()
                     if l.startswith("| `") and "SIMULADO" in l]
        if simulados:
            print("\nAVISO: los capítulos se han ejecutado con estos ficheros SIMULADOS:")
            print("   " + ", ".join(simulados))
            print("Ejecuta antes scripts/descargar_datos.py para usar datos reales donde sea posible.")
