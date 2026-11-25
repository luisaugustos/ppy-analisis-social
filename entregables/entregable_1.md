# Entregable 1 · Mis funciones para leer y resumir datos

**SE1 (problemas) · un tercio del 30 %** · Cubre las sesiones 2, 3 y 4.
Se publica el viernes 11 de diciembre de 2026. Entrega propuesta: domingo 10 de enero de 2027, 23:59, en el campus virtual de tu universidad.
Trabajo individual o en parejas.

## Qué hay que entregar

1. Un **módulo** `mis_funciones.py` con tus funciones, cada una con su *docstring*.
2. Un **notebook** que importa el módulo y lo usa, y que se ejecuta de principio a fin sin errores.
3. Un informe breve (máximo dos páginas, PDF) con los resultados y las decisiones que has tomado.

No se valora la cantidad de código, sino que sea tuyo, se entienda y funcione.

## Parte A · Funciones de cálculo (sesión 2)

1. `media_ponderada(valores, pesos)` y `gini_ponderado(rentas, pesos)`, sin bucles.
2. Al menos dos comprobaciones (`assert`) por función con casos de respuesta conocida.
3. Con el fichero de hogares de la Encuesta de Condiciones de Vida (el del curso o los microdatos reales del INE, indicando cuál), una tabla con la renta equivalente media y el Gini de cada región.

## Parte B · Leer un CSV y una API (sesión 3)

4. Elige en la web del INE una tabla que te interese, distinta de la de hipotecas, y anota su identificador.
5. Escribe `descargar_tabla(id_tabla)`, que la descargue de la API, la convierta en una tabla de pandas y **guarde una copia local**; si la copia ya existe, debe leerla en lugar de descargar.
6. Descarga a mano el CSV de esa misma tabla y escribe `leer_csv_ine(ruta)`, que lo lea y lo deje limpio (tipos correctos, fechas como fechas, valores perdidos reconocidos).
7. Comprueba con código que las dos funciones devuelven los mismos valores para un periodo.

## Parte C · Unir y resumir (sesión 4)

8. Con las hipotecas por provincia y la población, construye la tabla anual con hipotecas por mil habitantes. La unión debe usar `validate` y debes explicar qué haces con las filas sin pareja.
9. Indica la posición de tu provincia (o la que elijas) en el último año completo.
10. Guarda la tabla final en Parquet.

## Criterios de evaluación

| Criterio | Peso |
| --- | --- |
| Las funciones hacen lo que dicen y están comprobadas | 35 % |
| Organización: módulo, nombres claros, *docstrings*, sin código repetido ni rutas absolutas | 30 % |
| Decisiones explicadas (perdidos, filas sin pareja, años incompletos) | 25 % |
| Informe y cita de las fuentes | 10 % |

Indica siempre si has trabajado con datos reales o con los ficheros simulados del curso. Los resultados obtenidos con datos simulados no pueden presentarse como reales.
