# Entregable 2 · Funciones que dibujan y un flujo de exploración

**SE1 (problemas) · un tercio del 30 %** · Cubre las sesiones 5 y 6.
Se publica el viernes 18 de diciembre de 2026. Entrega propuesta: domingo 17 de enero de 2027, 23:59, en el campus virtual de tu universidad.
Trabajo individual o en parejas.

## Qué hay que entregar

1. Un módulo `.py` con tus funciones (puedes ampliar el del entregable 1).
2. Un notebook que lo usa y se ejecuta de principio a fin sin errores.
3. Un informe breve (máximo dos páginas, PDF) con las figuras y su lectura.
4. Opcional y valorado: una aplicación de Streamlit (fichero `.py`).

## Parte A · Funciones que dibujan (sesión 5)

1. Una función `grafico_serie(tabla, territorio, ax=None)` que dibuje una serie temporal con su media móvil, con título, unidades y eje adecuado.
2. Una figura con **cuatro paneles** hecha llamando a esa función en un bucle, guardada como imagen desde el código.
3. Una función que compare varios territorios usando **tasas**, no totales.
4. Una versión interactiva de uno de los gráficos con Plotly.

Puedes usar la serie de hipotecas o la tabla que descargaste en el entregable 1.

## Parte B · Un flujo de exploración (sesión 6)

Con un barómetro del CIS descargado por ti (indica el número de estudio) o, si no es posible, con el barómetro del curso:

5. Al menos **tres pasos de preparación**, cada uno una función que recibe una tabla y devuelve otra (etiquetas, no respuesta, agrupaciones…), encadenados con `.pipe`.
6. Una función que calcule un porcentaje ponderado por grupos y devuelva también el número de entrevistas. Úsala con dos variables de agrupación distintas.
7. Un análisis de la no respuesta de una pregunta: ¿quién no contesta?
8. Tres frases que respondan a una pregunta que te hayas planteado, distinguiendo lo que los datos permiten afirmar de lo que solo sugieren.

## Criterios de evaluación

| Criterio | Peso |
| --- | --- |
| Funciones reutilizables: se usan más de una vez, con parámetros en lugar de copiar y pegar | 35 % |
| Corrección: pesos, no respuesta, tasas, ejes y unidades | 30 % |
| Interpretación prudente | 20 % |
| Reproducibilidad y cita de las fuentes | 15 % |
| Aplicación de Streamlit | hasta +1 punto |

Una aplicación pública no puede contener microdatos con licencia, solo fuentes abiertas o resultados agregados.
