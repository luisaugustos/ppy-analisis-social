"""Funciones para trabajar con los datos de vivienda del curso."""
import pandas as pd


def leer_hipotecas(ruta="datos/hipotecas.csv"):
    """Lee las hipotecas mensuales por provincia, sin el total nacional."""
    tabla = pd.read_csv(ruta, dtype={"cod_prov": str}, parse_dates=["fecha"])
    tabla = tabla[tabla["cod_prov"] != "00"]
    tabla["anyo"] = tabla["fecha"].dt.year
    return tabla


def resumen_anual(hipotecas):
    """Suma las hipotecas de cada provincia por año y se queda con los años completos."""
    anual = (
        hipotecas
        .groupby(["cod_prov", "provincia", "ccaa", "anyo"], as_index=False)
        .agg(hipotecas=("hipotecas", "sum"), importe_miles=("importe_miles", "sum"), meses=("fecha", "count"))
    )
    return anual[anual["meses"] == 12].drop(columns="meses")


def anadir_tasa(anual, ruta_poblacion="datos/poblacion.csv"):
    """Añade la población y las hipotecas por mil habitantes.

    En los años sin dato de población se usa el último conocido de cada provincia.
    """
    poblacion = pd.read_csv(ruta_poblacion, dtype={"cod_prov": str})
    union = anual.merge(poblacion[["cod_prov", "anyo", "poblacion"]], on=["cod_prov", "anyo"],
                        how="left", validate="one_to_one")
    union = union.sort_values(["cod_prov", "anyo"])
    union["poblacion"] = union.groupby("cod_prov")["poblacion"].ffill()
    union["tasa_mil"] = union["hipotecas"] / union["poblacion"] * 1000
    return union
