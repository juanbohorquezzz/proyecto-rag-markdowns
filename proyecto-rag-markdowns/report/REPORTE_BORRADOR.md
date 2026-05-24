# Sistema RAG para investigar capital-trabajo, automatizacion y wage markdowns

**Integrantes:** Juan Bohorquez y Samuel Peña  
**Fecha:** pendiente  
**Curso:** Parcial 2 - Proyecto RAG

## 1. Introduccion

Este proyecto desarrolla un sistema Retrieval-Augmented Generation (RAG) para apoyar una investigacion economica sobre la relacion entre intensidad de capital, automatizacion y poder de negociacion laboral. La pregunta de investigacion futura es: como afecta el ratio capital-trabajo (K/L) al poder de negociacion de los trabajadores, medido por el wage markdown?

Un LLM generico no es suficiente para este problema porque puede confundir conceptos tecnicos como wage markdown, markup, monopsonio, elasticidad de sustitucion y capital stock. Tambien puede inventar resultados empiricos o citar fuentes inexistentes. RAG es adecuado porque permite generar respuestas basadas en documentos verificables, manteniendo trazabilidad de las fuentes.

## 2. Dataset y documentos

El sistema utiliza documentos academicos y fuentes oficiales sobre wage markdowns, automatizacion por tareas, Penn World Table, GDP per capita PPP y regulacion laboral. Los datos estructurados iniciales incluyen:

- Wage markdown mediano por pais desde la Table A.2 de Amodio et al. (2024).
- Penn World Table con `cn`, `emp`, `pop`, `pl_i` y `pl_gdpo`.
- World Bank WDI para GDP per capita PPP constante.
- OECD EPL index como medida de rigidez/proteccion laboral.

La base empirica preliminar cubre 82 paises en la tabla de markdowns y 79 paises con variables centrales completas para el periodo 2006-2019.

## 3. Arquitectura del sistema

El pipeline RAG sigue estas etapas:

1. Descarga o carga de documentos reales.
2. Extraccion de texto desde PDFs y HTML.
3. Limpieza basica del texto.
4. Chunking con fragmentos de 350 palabras y overlap de 70 palabras.
5. Generacion de embeddings con `intfloat/multilingual-e5-small`.
6. Almacenamiento vectorial con FAISS.
7. Recuperacion top-K con similitud coseno.
8. Generacion de respuestas con un LLM via API.
9. Evaluacion cualitativa de respuestas y trazabilidad.

El modelo de embeddings es un encoder: transforma texto en vectores semanticos. El modelo generador es un decoder/LLM: produce respuestas a partir de la pregunta y los fragmentos recuperados.

## 4. Resultados esperados

El sistema se evaluara con preguntas como:

- Que es un wage markdown y como se relaciona con el poder de negociacion laboral?
- Como conecta la automatizacion por tareas con la sustitucion entre capital y trabajo?
- Que evidencia existe sobre wage markdowns en paises de ingreso bajo y medio?
- Como se mide el ratio capital-trabajo usando Penn World Table?
- Que es el indice OECD EPL y por que podria importar para la heterogeneidad institucional?

Tambien se incluye un caso de fallo:

- Cual es el efecto causal exacto de aumentar K/L en 10% sobre el wage markdown de Colombia en 2024?

La respuesta esperada en este ultimo caso es que el sistema no puede identificar un efecto causal exacto con los documentos disponibles.

## 5. Extension empirica exploratoria

Como puente hacia un paper futuro, el notebook construye una base cross-country para 2006-2019:

- `log(markdown)` usando el p50 de Amodio et al.
- `log(K/L)` usando `cn / emp` de Penn World Table.
- `log(GDPpc)` usando GDP per capita PPP de WDI.

Se estiman tres especificaciones OLS exploratorias:

1. `log(markdown_c) = alpha + beta_1 log(K/L)_c + error_c`
2. `log(markdown_c) = alpha + beta_1 log(K/L)_c + beta_2 log(GDPpc)_c + error_c`
3. `log(markdown_c) = alpha + beta_1 log(K/L)_c + beta_2 log(K/L)_c^2 + beta_3 log(GDPpc)_c + error_c`

El modelo central futuro es el tercero. La prediccion teorica es `beta_1 > 0` y `beta_2 < 0`, consistente con una relacion no lineal.

## 6. Limitaciones

- La seccion empirica es exploratoria y no identifica causalidad.
- Falta incorporar una fuente tabular clara de wage markdowns para paises ricos/OECD.
- Algunas fuentes pueden estar en HTML y no PDF, lo que puede generar texto mas ruidoso.
- La calidad del RAG depende de la extraccion de texto, el chunking y la relevancia de los documentos cargados.
- Un valor de K demasiado bajo puede omitir contexto relevante; un K demasiado alto puede introducir ruido en el prompt.

## 7. Conclusiones

El proyecto construye un RAG funcional y trazable para apoyar investigacion economica sobre automatizacion, intensidad de capital y poder de negociacion laboral. Aunque el trabajo del curso se centra en el pipeline RAG, la estructura queda alineada con una investigacion futura sobre la relacion no lineal entre K/L y wage markdowns.

## 8. Bibliografia inicial

Ver `docs/SOURCE_INVENTORY.md`.

