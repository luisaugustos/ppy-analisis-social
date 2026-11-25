# Datos

Los notebooks leen los ficheros de esta carpeta con rutas relativas (`datos/hipotecas.csv`). La tabla de [ORIGEN.md](ORIGEN.md) indica cuáles son **reales** y cuáles **simulados**.

- Los ficheros simulados tienen la misma forma que los reales, pero valores inventados. Sirven para practicar sin conexión y sin redistribuir microdatos con licencia. No deben citarse como datos.
- `scripts/descargar_datos.py` (profesorado) sustituye por datos reales los que proceden de fuentes abiertas: hipotecas y población (INE), euríbor (Banco de España) y esperanza de vida (Our World in Data).
- Lo que descargan los estudiantes con su propio código se guarda en `datos/descargas/`, que no se sube a GitHub.

## Fuentes que descarga cada persona

- **Barómetros del CIS** (`.sav`): registro gratuito en cis.es. No se redistribuyen.
- **Encuesta de Condiciones de Vida** (INE, microdatos): descarga libre desde INEbase → Nivel y condiciones de vida → ECV → Microdatos. Del fichero de hogares se usan `DB040`, `DB090`, `HY020`, `HX040` y `HX240`.
- **Atlas de distribución de renta de los hogares** (INE): renta neta media por persona por provincia y año.
