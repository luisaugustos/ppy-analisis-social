# Programación avanzada en Python aplicada al análisis social

Materiales de la asignatura optativa del Máster en Ciencia de Datos aplicada a las Ciencias Sociales (Universidad de Granada y Universidad de Salamanca), curso 2026-27. Once sesiones síncronas de dos horas, en línea por Google Meet; ver [CALENDARIO.md](CALENDARIO.md).

## Planteamiento

El hilo de la asignatura es pasar **del notebook suelto al código organizado**. Los estudiantes no reciben una librería hecha: escriben sus propias funciones para leer un CSV, consultar una API, unir tablas, dibujar y explorar, y las van guardando en módulos suyos. Está pensada para un alumnado sin perfil informático: cada sesión introduce una sola idea de programación nueva.

Como caso de estudio se usa el **acceso a la vivienda**: hipotecas por provincia (INE), euríbor (Banco de España), población y renta.

### Relación con otras asignaturas del máster

| Asignatura | Lo que se da allí | Lo que hacemos aquí |
| --- | --- | --- |
| Fundamentos de programación | Bases de Python y R | Un refresco en la sesión 1; se dan por sabidas |
| Fundamentos de aprendizaje estadístico | Descriptiva, inferencia, regresión, series | Programar estadísticos como funciones; sin inferencia |
| Obtención, almacenamiento y preprocesamiento | ETL, *scraping*, SQL y NoSQL, métodos de limpieza | Leer CSV y una API con pandas y `requests` |
| Fundamentos de aprendizaje automático | Algoritmos y evaluación de modelos | Organizar el código de un modelo (`Pipeline`) |
| Análisis de textos y redes sociales | PLN y redes | No se trata |
| Visualización de datos sociales digitales | Diseño de visualizaciones | Funciones que dibujan y una app mínima |

## Contenido

| Carpeta | Qué hay |
| --- | --- |
| `sesiones/sNN_…/` | Diapositivas (`.pptx`), notebook de teoría, notebook de práctica con `# TODO` y práctica resuelta |
| `datos/` | Ficheros de datos de las sesiones; [datos/ORIGEN.md](datos/ORIGEN.md) dice cuáles son reales y cuáles simulados |
| `entregables/`, `debates/`, `proyecto/` | Enunciados evaluables, preguntas de debate y guía del proyecto final |
| `apps/` | Plantilla de aplicación Streamlit |
| `scripts/`, `_fuente/`, `_profesorado/` | Solo profesorado: construcción y prueba de notebooks, descarga de datos y soluciones de referencia |

## Cómo trabajar

**En Google Colab.** Abre el notebook desde GitHub y ejecuta la primera celda de código, que descarga esta carpeta. 

**En local, con `uv`.**

```bash
git clone https://github.com/luisaugustos/ppy-analisis-social.git
cd ppy-analisis-social
uv sync
uv run jupyter lab
uv run streamlit run apps/app_plantilla.py   # la app no funciona en Colab
```

## Para el profesorado

```bash
uv run python scripts/descargar_datos.py       # sustituye los datos simulados por datos reales (INE, BdE, OWID)
uv run python scripts/construir_notebooks.py   # regenera los .ipynb a partir de _fuente/
uv run python scripts/probar_notebooks.py      # ejecuta teoría y prácticas resueltas de principio a fin
uv run python scripts/construir_libro.py --ejecutar   # genera los capítulos del libro (TeachBook)
```

Cada sesión se edita en `_fuente/sNN_teoria.txt` y `_fuente/sNN_practica.txt`. En las prácticas, el código entre `#>>>` y `#<<<` es la solución, que se elimina en la versión para estudiantes. Si el repositorio va a ser público antes de clase, excluye `_fuente/`, `_profesorado/` y los `*_practica_resuelta.ipynb`.

## Evaluación

| Sistema | Peso | Qué es |
| --- | --- | --- |
| SE1 · Problemas | 30 % | Tres entregables con informe breve |
| SE4 · Debates virtuales | 20 % | Un debate en el foro tras cada bloque |
| SE10 · Proyecto final | 50 % | Se propone en la sesión 7 y se defiende en la 11 |
