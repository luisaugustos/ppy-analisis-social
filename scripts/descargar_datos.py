"""(Profesorado) Sustituye los ficheros simulados de datos/ por datos reales de las fuentes abiertas.

    uv run python scripts/descargar_datos.py

Descarga hipotecas y población (API del INE), euríbor (Banco de España) y esperanza
de vida (Our World in Data), los guarda con el mismo formato que usan los notebooks y
actualiza datos/ORIGEN.md. Lo que no se puede descargar se queda como estaba.
Los estudiantes no usan este script: aprenden a descargar por su cuenta en la sesión 3.
"""
import io
import json
import sys
import warnings
from datetime import date
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "_profesorado"))
sys.path.insert(0, str(RAIZ / "scripts"))
from ppy import datos as ref  # noqa: E402
import generar_muestras as gm  # noqa: E402

DATOS = RAIZ / "datos"
HOY = date.today().isoformat()


def hipotecas():
    df = ref._hipotecas_ine()
    naturalezas = list(df["naturaleza"].dropna().unique())
    elegida = "Viviendas" if "Viviendas" in naturalezas else ("Total fincas" if "Total fincas" in naturalezas else naturalezas[0])
    df = df[(df["naturaleza"] == elegida) & (df["fecha"] >= "2011-01-01")].reset_index(drop=True)
    df.to_csv(DATOS / "hipotecas.csv", index=False)
    gm.ine_bruto(df).to_csv(DATOS / "ine_hipotecas_bruto.csv", index=False, sep=";", encoding="latin-1")
    (DATOS / "ine_respuesta_ejemplo.json").write_text(json.dumps(gm.ine_json(df), ensure_ascii=False, indent=1), encoding="utf-8")
    return f"INE, Estadística de Hipotecas, tabla 3200, «{elegida}» (descargado el {HOY})", df


def poblacion():
    df = ref._poblacion_ine()
    df.to_csv(DATOS / "poblacion.csv", index=False)
    return f"INE, Padrón, tabla 2852 (descargado el {HOY})", df


def euribor():
    df = ref._euribor_bde()
    df = df[df["fecha"] >= "2011-01-01"]
    df.to_csv(DATOS / "euribor.csv", index=False)
    return f"Banco de España (descargado el {HOY})", df


def esperanza_vida():
    url = "https://ourworldindata.org/grapher/life-expectancy.csv?v=1&csvType=full&useColumnShortNames=true"
    df = pd.read_csv(io.StringIO(ref._descargar(url).text))
    df.to_csv(DATOS / "esperanza_vida.csv", index=False)
    return f"Our World in Data (descargado el {HOY})", df


if __name__ == "__main__":
    warnings.simplefilter("ignore")
    origen, fallos = {}, 0
    for clave, nombre, funcion in [("hip", "Hipotecas (INE)", hipotecas), ("pob", "Población (INE)", poblacion),
                                   ("eur", "Euríbor (Banco de España)", euribor), ("owid", "Esperanza de vida (OWID)", esperanza_vida)]:
        try:
            origen[clave], df = funcion()
            print(f"OK     {nombre:<28} {len(df):>7,} filas")
        except Exception as e:  # noqa: BLE001
            fallos += 1
            print(f"FALLO  {nombre:<28} {type(e).__name__}: {str(e)[:120]}")
    if origen:
        previo = (DATOS / "ORIGEN.md").read_text(encoding="utf-8")
        for clave, fichero in [("hip", "hipotecas.csv"), ("pob", "poblacion.csv"), ("eur", "euribor.csv"), ("owid", "esperanza_vida.csv")]:
            if clave not in origen:  # conserva lo que ya fuera real
                for linea in previo.splitlines():
                    if linea.startswith(f"| `{fichero}`") and "SIMULADO" not in linea:
                        origen[clave] = linea.split("|")[3].strip()
        gm.escribir_origen(**origen)
        print("\nActualizado datos/ORIGEN.md. Regenera después los notebooks del libro (scripts/construir_libro.py --ejecutar).")
    print("Siguen simulados: renta, ECV y barómetro (ver datos/README.md).")
    sys.exit(1 if fallos else 0)
