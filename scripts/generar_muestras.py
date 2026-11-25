"""Genera los ficheros SIMULADOS de datos/ (profesorado).

Los valores son inventados (con una forma verosímil) y solo sirven para que
los notebooks funcionen sin conexión. No deben usarse para sacar conclusiones.

    uv run python scripts/generar_muestras.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "_profesorado"))
from ppy.provincias import PROVINCIAS  # noqa: E402

SALIDA = RAIZ / "datos"
SALIDA.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2026)


def euribor() -> pd.DataFrame:
    """Trayectoria aproximada del euríbor a un año (puntos de anclaje interpolados)."""
    anclas = {"2011-01": 1.55, "2011-07": 2.18, "2012-06": 1.22, "2013-01": 0.58, "2014-06": 0.51,
              "2015-06": 0.16, "2016-02": -0.01, "2017-06": -0.15, "2018-06": -0.18, "2019-08": -0.36,
              "2020-04": -0.11, "2020-12": -0.50, "2021-12": -0.50, "2022-04": 0.01, "2022-09": 2.23,
              "2023-03": 3.65, "2023-10": 4.16, "2024-06": 3.65, "2024-12": 2.44, "2025-06": 2.08,
              "2025-12": 2.25, "2026-08": 3.00}
    s = pd.Series(anclas)
    s.index = pd.to_datetime(s.index)
    s = s.resample("MS").interpolate("linear")
    s = (s + rng.normal(0, 0.03, len(s))).round(3)
    return s.rename("euribor_12m").rename_axis("fecha").reset_index()


def hipotecas(eur: pd.DataFrame) -> pd.DataFrame:
    fechas = pd.date_range("2011-01-01", "2026-08-01", freq="MS")
    t = np.arange(len(fechas))
    # tendencia nacional: caída 2011-2013, recuperación, parón de 2020, rebote y freno por tipos
    anclas = {"2011-01": 1.45, "2013-06": 0.62, "2016-01": 0.85, "2019-06": 1.10, "2021-06": 1.25,
              "2022-06": 1.42, "2023-09": 1.08, "2025-01": 1.35, "2026-08": 1.50}
    tend = pd.Series(anclas)
    tend.index = pd.to_datetime(tend.index)
    tend = tend.reindex(fechas).interpolate("time").to_numpy()
    estacional = 1 + 0.08 * np.cos(2 * np.pi * (fechas.month - 3) / 12) - 0.12 * (fechas.month == 8)
    covid = np.ones(len(fechas))
    covid[(fechas == "2020-04-01")] = 0.55
    covid[(fechas == "2020-05-01")] = 0.60
    covid[(fechas == "2020-06-01")] = 0.82
    filas = []
    for p in PROVINCIAS.itertuples():
        propension = rng.uniform(0.55, 0.95)  # hipotecas mensuales por mil habitantes, aprox.
        costa = 1.25 if p.cod_prov in {"03", "07", "29", "35", "38", "17", "43"} else 1.0
        base = p.pob_miles * propension * costa
        ruido = rng.lognormal(0, 0.10 + 0.9 / np.sqrt(p.pob_miles), len(t))
        n = np.maximum(np.round(base * tend * estacional * covid * ruido), 1).astype(int)
        precio = rng.uniform(85, 115) * (1.6 if p.cod_prov in {"28", "08", "07", "20"} else 1.0)
        importe_medio = precio * (1 + 0.025) ** (t / 12) * rng.normal(1, 0.03, len(t))  # miles de euros
        filas.append(pd.DataFrame({"fecha": fechas, "cod_prov": p.cod_prov, "provincia": p.provincia,
                                   "ccaa": p.ccaa, "naturaleza": "Viviendas", "hipotecas": n,
                                   "importe_miles": np.round(n * importe_medio).astype(int)}))
    df = pd.concat(filas, ignore_index=True)
    nac = (df.groupby("fecha", as_index=False)[["hipotecas", "importe_miles"]].sum()
           .assign(cod_prov="00", provincia="Total Nacional", ccaa="Total Nacional", naturaleza="Viviendas"))
    df = pd.concat([nac[df.columns], df], ignore_index=True)
    # unos pocos huecos para practicar valores perdidos
    huecos = df[df["cod_prov"].isin(["42", "44", "51", "52"])].sample(12, random_state=1).index
    df["hipotecas"] = df["hipotecas"].astype("Int64")
    df["importe_miles"] = df["importe_miles"].astype("Int64")
    df.loc[huecos, ["hipotecas", "importe_miles"]] = pd.NA
    return df


def poblacion() -> pd.DataFrame:
    filas = []
    for p in PROVINCIAS.itertuples():
        crec = rng.normal(0.002, 0.006)
        for anyo in range(2011, 2022):
            filas.append((p.cod_prov, p.provincia, anyo, int(p.pob_miles * 1000 * (1 + crec) ** (anyo - 2021))))
    return pd.DataFrame(filas, columns=["cod_prov", "provincia", "anyo", "poblacion"])


def renta() -> pd.DataFrame:
    filas = []
    for p in PROVINCIAS.itertuples():
        nivel = rng.normal(12500, 1300)
        if p.ccaa in {"País Vasco", "Comunidad Foral de Navarra", "Comunidad de Madrid", "Cataluña"}:
            nivel += 2800
        if p.ccaa in {"Andalucía", "Extremadura", "Canarias", "Región de Murcia"}:
            nivel -= 1500
        for anyo in range(2015, 2025):
            filas.append((p.cod_prov, p.provincia, anyo, int(nivel * 1.035 ** (anyo - 2020) * rng.normal(1, 0.01))))
    return pd.DataFrame(filas, columns=["cod_prov", "provincia", "anyo", "renta_neta_persona"])


def ecv(n: int = 4000) -> pd.DataFrame:
    regiones = ["ES11", "ES12", "ES13", "ES21", "ES22", "ES23", "ES24", "ES30", "ES41", "ES42",
                "ES43", "ES51", "ES52", "ES53", "ES61", "ES62", "ES70"]
    efecto = dict(zip(regiones, rng.normal(0, 0.12, len(regiones))))
    efecto.update({"ES21": 0.25, "ES30": 0.22, "ES22": 0.2, "ES61": -0.18, "ES43": -0.2})
    reg = rng.choice(regiones, n)
    miembros = rng.choice([1, 2, 3, 4, 5, 6], n, p=[0.26, 0.31, 0.20, 0.17, 0.045, 0.015])
    menores = np.array([rng.binomial(max(m - 1, 0), 0.3) for m in miembros])
    uc = 1 + 0.5 * (miembros - 1 - menores) + 0.3 * menores
    renta_uc = rng.lognormal(np.log(17500) + np.vectorize(efecto.get)(reg), 0.55, n)
    hy020 = np.round(renta_uc * uc, 2)
    hy020[rng.random(n) < 0.004] *= -0.1  # algunas rentas negativas, como en la encuesta real
    return pd.DataFrame({"DB030": np.arange(1, n + 1), "DB040": reg,
                         "DB090": np.round(rng.lognormal(np.log(4700), 0.45, n), 4),
                         "HY020": np.round(hy020, 2), "HX040": miembros, "HX240": np.round(uc, 1)})


def cis(n: int = 2500):
    import pyreadstat

    ccaa = rng.choice(np.arange(1, 18), n, p=np.array([18, 3, 2, 3, 5, 1, 4, 5, 16, 11, 2, 6, 14, 3, 1.5, 4.8, 0.7]) / 100)
    edad = np.clip(rng.normal(50, 18, n).round(), 18, 95).astype(int)
    sexo = rng.choice([1, 2], n, p=[0.48, 0.52])
    estudios = np.clip(rng.choice([1, 2, 3, 4, 5, 6], n, p=[0.05, 0.15, 0.22, 0.20, 0.14, 0.24]) - (edad > 70), 1, 6)
    ideol = np.clip(rng.normal(4.7, 2.1, n).round(), 1, 10)
    ideol[rng.random(n) < 0.10] = 98
    ideol[rng.random(n) < 0.06] = 99
    # preocupación por la vivienda: mayor entre jóvenes
    p_viv = 0.12 + 0.25 * (edad < 35) + 0.08 * (edad < 50)
    vivienda = (rng.random(n) < p_viv).astype(int)
    sit = np.clip(rng.normal(3.1 + 0.25 * vivienda - 0.08 * estudios, 1, n).round(), 1, 5)
    sit[rng.random(n) < 0.03] = 8
    sit[rng.random(n) < 0.01] = 9
    tenencia = np.where(edad < 35, rng.choice([1, 2, 3], n, p=[0.25, 0.50, 0.25]),
                        rng.choice([1, 2, 3], n, p=[0.78, 0.17, 0.05]))
    # la muestra sobrerrepresenta estudios altos: el peso lo corrige
    peso = np.where(estudios >= 5, 0.72, 1.18) * rng.normal(1, 0.08, n)
    peso = peso / peso.mean()
    df = pd.DataFrame({"CUES": np.arange(1, n + 1), "CCAA": ccaa, "SEXO": sexo, "EDAD": edad,
                       "ESTUDIOS": estudios, "ESCIDEOL": ideol, "SITECON": sit, "PROBVIV": vivienda,
                       "TENENCIA": tenencia, "PESO": peso.round(4)}).astype({"ESCIDEOL": int, "SITECON": int})
    nombres_ccaa = ["Andalucía", "Aragón", "Asturias", "Balears", "Canarias", "Cantabria", "Castilla-La Mancha",
                    "Castilla y León", "Cataluña", "Comunitat Valenciana", "Extremadura", "Galicia", "Madrid",
                    "Murcia", "Navarra", "País Vasco", "La Rioja"]
    etiquetas_var = {"CUES": "Número de cuestionario", "CCAA": "Comunidad autónoma", "SEXO": "Sexo",
                     "EDAD": "Edad de la persona entrevistada", "ESTUDIOS": "Nivel de estudios alcanzado",
                     "ESCIDEOL": "Escala de autoubicación ideológica (1-10)",
                     "SITECON": "Valoración de la situación económica personal",
                     "PROBVIV": "Menciona la vivienda entre los principales problemas",
                     "TENENCIA": "Régimen de tenencia de la vivienda", "PESO": "Ponderación"}
    etiquetas_val = {
        "CCAA": dict(enumerate(nombres_ccaa, start=1)),
        "SEXO": {1: "Hombre", 2: "Mujer"},
        "ESTUDIOS": {1: "Sin estudios", 2: "Primaria", 3: "Secundaria 1ª etapa", 4: "Secundaria 2ª etapa",
                     5: "FP superior", 6: "Universitarios"},
        "ESCIDEOL": {1: "1 Izquierda", 10: "10 Derecha", 98: "N.S.", 99: "N.C."},
        "SITECON": {1: "Muy buena", 2: "Buena", 3: "Regular", 4: "Mala", 5: "Muy mala", 8: "N.S.", 9: "N.C."},
        "PROBVIV": {0: "No menciona", 1: "Menciona"},
        "TENENCIA": {1: "En propiedad", 2: "En alquiler", 3: "Cedida u otra situación"},
    }
    pyreadstat.write_sav(df, str(SALIDA / "barometro.sav"), file_label="Barómetro SIMULADO (PPY)",
                         column_labels=etiquetas_var, variable_value_labels=etiquetas_val)


def owid() -> pd.DataFrame:
    paises = {"Spain": ("ESP", 82.3), "Portugal": ("PRT", 80.5), "France": ("FRA", 82.0), "Germany": ("DEU", 80.6),
              "Italy": ("ITA", 82.4), "Brazil": ("BRA", 73.5), "United States": ("USA", 78.6),
              "Japan": ("JPN", 83.6), "Nigeria": ("NGA", 51.5), "India": ("IND", 67.5), "World": ("OWID_WRL", 70.8)}
    filas = []
    for pais, (cod, v2011) in paises.items():
        for anyo in range(1990, 2024):
            v = v2011 + 0.2 * (anyo - 2011) - (1.2 if anyo in (2020, 2021) else 0) + rng.normal(0, 0.1)
            filas.append((pais, cod, anyo, round(v, 2)))
    return pd.DataFrame(filas, columns=["Entity", "Code", "Year", "life_expectancy_0"])


def ine_bruto(hip: pd.DataFrame) -> pd.DataFrame:
    """Las mismas hipotecas con el aspecto de un CSV descargado de la web del INE."""
    d = hip[hip["fecha"] >= "2024-01-01"].copy()
    d["Provincias"] = np.where(d["cod_prov"] == "00", "Total Nacional", d["cod_prov"] + " " + d["provincia"])
    d["Periodo"] = d["fecha"].dt.strftime("%YM%m")
    largo = d.melt(id_vars=["Provincias", "Periodo"], value_vars=["hipotecas", "importe_miles"],
                   var_name="Concepto", value_name="Total")
    largo["Concepto"] = largo["Concepto"].map({"hipotecas": "Número de hipotecas", "importe_miles": "Importe de hipotecas"})
    largo["Naturaleza de la finca"] = "Viviendas"

    def formato(v):
        return ".." if pd.isna(v) else f"{int(v):,}".replace(",", ".")

    largo["Total"] = largo["Total"].map(formato)
    return largo[["Provincias", "Naturaleza de la finca", "Concepto", "Periodo", "Total"]]


def ine_json(hip: pd.DataFrame) -> list:
    """Respuesta de ejemplo con la estructura de la API JSON del INE (tabla 3200, tres últimos meses)."""
    ultimos = sorted(hip["fecha"].unique())[-3:]
    series = []
    for cod in ["00", "18", "28", "37"]:
        d = hip[(hip["cod_prov"] == cod) & hip["fecha"].isin(ultimos)]
        nombre = d["provincia"].iloc[0]
        for concepto, col in [("Número de hipotecas", "hipotecas"), ("Importe de hipotecas", "importe_miles")]:
            series.append({
                "COD": f"HPT{cod}{col[:3].upper()}",
                "Nombre": f"Viviendas. {concepto}. {nombre}. Base nueva. Mensual. ",
                "T3_Unidad": "Hipotecas" if col == "hipotecas" else "Euros",
                "T3_Escala": " " if col == "hipotecas" else "Miles",
                "MetaData": [
                    {"Id": 1, "T3_Variable": "Naturaleza de la finca", "Nombre": "Viviendas", "Codigo": ""},
                    {"Id": 2, "T3_Variable": "Concepto financiero", "Nombre": concepto, "Codigo": ""},
                    {"Id": 3, "T3_Variable": "Total Nacional" if cod == "00" else "Provincias", "Nombre": nombre, "Codigo": cod},
                ],
                "Data": [{"Fecha": f"{f:%Y-%m-%d}T00:00:00.000+02:00", "T3_TipoDato": "Provisional",
                          "T3_Periodo": f"M{f:%m}", "Anyo": int(f.year), "Valor": float(v)}
                         for f, v in zip(d["fecha"], d[col])][::-1],
            })
    return series


ORIGEN = """# Origen de los ficheros de esta carpeta

| Fichero | Contenido | Origen |
| --- | --- | --- |
| `hipotecas.csv` | Hipotecas mensuales sobre viviendas por provincia | {hip} |
| `ine_hipotecas_bruto.csv` | Las mismas hipotecas desde 2024, con el formato de descarga del INE | {hip} |
| `ine_respuesta_ejemplo.json` | Respuesta de ejemplo de la API del INE (tres meses, cuatro territorios) | {hip} |
| `poblacion.csv` | Población anual por provincia | {pob} |
| `euribor.csv` | Euríbor a un año, mensual | {eur} |
| `renta.csv` | Renta neta media por persona, por provincia y año | SIMULADO |
| `esperanza_vida.csv` | Esperanza de vida al nacer por país | {owid} |
| `ecv_hogares.csv` | Hogares con las variables de la Encuesta de Condiciones de Vida | SIMULADO |
| `barometro.sav` | Barómetro con la estructura de los del CIS | SIMULADO |

**SIMULADO** significa que los valores son inventados (con una forma verosímil) para poder
practicar sin conexión y sin redistribuir microdatos con licencia. No describen la realidad
y no deben citarse como datos.
"""


def escribir_origen(**real):
    campos = {k: real.get(k, "SIMULADO") for k in ("hip", "pob", "eur", "owid")}
    (SALIDA / "ORIGEN.md").write_text(ORIGEN.format(**campos), encoding="utf-8")


if __name__ == "__main__":
    import json

    eur = euribor()
    eur.to_csv(SALIDA / "euribor.csv", index=False)
    hip = hipotecas(eur)
    hip.to_csv(SALIDA / "hipotecas.csv", index=False)
    ine_bruto(hip).to_csv(SALIDA / "ine_hipotecas_bruto.csv", index=False, sep=";", encoding="latin-1")
    (SALIDA / "ine_respuesta_ejemplo.json").write_text(json.dumps(ine_json(hip), ensure_ascii=False, indent=1), encoding="utf-8")
    poblacion().to_csv(SALIDA / "poblacion.csv", index=False)
    renta().to_csv(SALIDA / "renta.csv", index=False)
    ecv().to_csv(SALIDA / "ecv_hogares.csv", index=False)
    owid().to_csv(SALIDA / "esperanza_vida.csv", index=False)
    cis()
    escribir_origen()
    for f in sorted(SALIDA.iterdir()):
        if f.is_file():
            print(f"{f.name:40s} {f.stat().st_size / 1024:8.1f} KB")
