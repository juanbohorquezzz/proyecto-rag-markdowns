# Sistema RAG para investigar capital-trabajo, automatizacion y wage markdowns

**Integrantes:** Juan Bohorquez y Samuel Peña  
**Curso:** Parcial 2 - Proyecto RAG  
**Fecha:** 2026

## 1. Introduccion

Este proyecto desarrolla un sistema Retrieval-Augmented Generation (RAG) para apoyar una investigacion economica sobre la relacion entre intensidad de capital, automatizacion y poder de negociacion laboral. La pregunta de investigacion futura es: como afecta el ratio capital-trabajo (K/L) al poder de negociacion de los trabajadores, medido por el wage markdown?

Un LLM generico no es suficiente para este problema porque puede confundir conceptos tecnicos como wage markdown, markup, monopsonio, elasticidad de sustitucion y capital stock. Tambien puede inventar resultados empiricos o atribuir conclusiones causales que no estan respaldadas por la literatura. RAG es adecuado porque obliga al sistema a recuperar primero fragmentos de documentos verificables y luego generar una respuesta condicionada a ese contexto.

Frente a fine-tuning, RAG es mas apropiado para este caso porque el objetivo no es cambiar los parametros del modelo, sino darle acceso a documentos especificos y actualizables: papers, documentacion de Penn World Table, World Bank WDI, OECD EPL y tablas de markdowns. Esto permite actualizar el corpus sin reentrenar un modelo.

## 2. Dataset y documentos

El sistema usa documentos academicos y fuentes oficiales sobre wage markdowns, automatizacion por tareas, Penn World Table, GDP per capita PPP y regulacion laboral.

Los documentos candidatos fueron:

| ID | Documento | Rol |
|---|---|---|
| D1 | Amodio et al. (2024), Table A.2 | Fuente central de wage markdowns por pais |
| D2 | Penn World Table 10.0 User Guide | Definicion y advertencias de variables PWT |
| D3 | Feenstra, Inklaar and Timmer (2015) | Fundamento metodologico de PWT |
| D4 | World Bank WDI GDPpc PPP | Metadatos de GDP per capita PPP |
| D5 | OECD Indicators of Employment Protection | Fuente del indice EPL |
| D6 | OECD Employment Outlook 2020 | Metodologia de EPL |
| D7 | Acemoglu and Restrepo (2019) | Marco teorico de automatizacion por tareas |
| D8 | Acemoglu and Restrepo, Robots and Jobs | Evidencia sobre robots, empleo y salarios |
| D9 | Oberfield and Raval | Elasticidad de sustitucion capital-trabajo |
| D10 | Diez, Leigh and Tambunlertchai (2018) | Poder de mercado, inversion y labor share |

En la corrida final corregida, 8 documentos web/PDF tuvieron texto extraible o fueron cargados manualmente. OECD Employment Outlook 2020 se incorporo como PDF manual en D6. Dos fuentes no entraron directamente al corpus por bloqueos 403 o descarga fallida: OECD EPL web e IMF Global Market Power. Para corregir la limitacion de OECD EPL, se agregaron dos documentos estructurados construidos desde datos locales: D11, con la Table A.2 de Amodio et al., y D12, con el CSV de OECD EPL.

Ademas, se usaron datos estructurados:

- Table A.2 de Amodio et al. (2024): markdown p25, p50 y p75 por pais.
- Penn World Table: `cn`, `emp`, `pop`, `pl_i`, `pl_gdpo`.
- World Bank WDI: GDP per capita PPP constante.
- OECD EPL: indicador de rigidez/proteccion laboral.

## 3. Arquitectura del sistema

El pipeline implementado fue:

1. Descarga o carga de documentos reales.
2. Extraccion de texto desde PDFs y HTML.
3. Limpieza basica del texto.
4. Chunking con fragmentos de 350 palabras y overlap de 70 palabras.
5. Generacion de embeddings con `intfloat/multilingual-e5-small`.
6. Almacenamiento vectorial con FAISS.
7. Recuperacion top-K con ranking hibrido: similitud coseno + boost lexico por terminos de dominio.
8. Generacion de respuesta condicionada al contexto recuperado.
9. Evaluacion cualitativa de respuestas y trazabilidad.

El modelo de embeddings es un encoder: transforma textos y preguntas en vectores semanticos. La dimensionalidad reportada fue 384 y la longitud maxima del encoder fue 512 tokens. La base vectorial FAISS almaceno 1010 vectores despues de agregar los documentos estructurados D11 y D12 y el PDF manual D6.

El valor usado para recuperacion fue `K = 5`. Este valor permite recuperar varias fuentes sin saturar el prompt con demasiado ruido. Si K es muy bajo, puede faltar contexto; si K es muy alto, entran fragmentos menos relevantes y la respuesta puede desviarse.

## 4. Procesamiento de documentos

La estrategia de chunking uso 350 palabras con 70 palabras de overlap. En la version corregida se generaron 1010 chunks. El aumento respecto a la primera corrida se explica principalmente por la incorporacion manual del PDF OECD Employment Outlook 2020, que aporto mas de un millon de caracteres extraidos, y por los documentos estructurados D11 y D12. Esto fortalecio la recuperacion de preguntas sobre markdowns y EPL.

El trade-off del chunking es central: chunks muy pequenos pueden perder definiciones o argumentos completos; chunks muy grandes pueden mezclar temas y reducir la precision de la busqueda semantica. El overlap ayuda a conservar continuidad entre fragmentos vecinos.

## 5. Resultados del RAG

La evaluacion uso seis preguntas: cinco representativas y un caso de fallo. Los resultados muestran que la recuperacion funciono mejor despues de agregar documentos estructurados desde los CSVs centrales y de usar ranking hibrido.

| Pregunta | Top docs | Score maximo | Evaluacion |
|---|---|---:|---|
| Que es un wage markdown y como se relaciona con el poder de negociacion laboral? | D11, D11, D11, D11, D7 | 1.835 | Buena: recupera Amodio estructurado y conecta markdown con bargaining. |
| Como conecta la automatizacion por tareas con la sustitucion entre capital y trabajo? | D7 repetido | 1.514 | Buena: recupera el documento teorico correcto de Acemoglu y Restrepo. |
| Que evidencia existe sobre wage markdowns en paises de ingreso bajo y medio? | D11, D11, D11, D11, D1 | 1.834 | Buena: recupera Table A.2 estructurada de Amodio. |
| Como se mide el ratio capital-trabajo usando Penn World Table? | D3, D3, D2, D3, D3 | 1.400 | Buena: recupera la guia PWT y el paper metodologico. |
| Que es el indice OECD EPL y por que podria importar para la heterogeneidad institucional? | D12, D12, D6, D6, D6 | 1.713 | Buena: recupera el documento estructurado OECD EPL y el PDF de OECD Employment Outlook 2020. |
| Efecto causal exacto de aumentar K/L en 10% sobre el markdown de Colombia en 2024 | D11, D11, D11, D11, D3 | 1.819 | Buen caso de fallo: el sistema no afirma causalidad exacta. |

La API LLM fallo por falta de cuota, por lo que la corrida final uso un modo local de respaldo. Esto no reemplaza completamente la generacion por LLM, pero conserva la parte central del RAG: recuperacion, scores, fragmentos y trazabilidad. Para una entrega ideal, se recomienda ejecutar la misma arquitectura con una API con cuota disponible o con un generador local.

## 6. Extension empirica exploratoria

Como puente hacia el paper futuro, el notebook construyo una base cross-country para 2006-2019. La muestra incluyo 82 paises en la tabla de Amodio, de los cuales 79 tuvieron variables completas para `markdown`, `K/L` y `GDPpc`.

Variables:

- `log(markdown)`: logaritmo del p50 de Amodio et al.
- `log(K/L)`: logaritmo de `cn / emp` desde Penn World Table.
- `log(GDPpc)`: logaritmo del GDP per capita PPP desde WDI.

Se estimaron tres especificaciones OLS:

| Modelo | Termino | Estimacion | Error estandar | t |
|---|---|---:|---:|---:|
| M1 | log(K/L) | 0.0358 | 0.0347 | 1.032 |
| M2 | log(K/L) | 0.1002 | 0.0789 | 1.270 |
| M2 | log(GDPpc) | -0.0884 | 0.0973 | -0.909 |
| M3 | log(K/L) | 1.0936 | 0.7146 | 1.530 |
| M3 | log(K/L)^2 | -0.0453 | 0.0324 | -1.399 |
| M3 | log(GDPpc) | -0.0873 | 0.0967 | -0.903 |

El modelo M3 es el mas cercano a la hipotesis futura. Los signos obtenidos son consistentes con la prediccion teorica: coeficiente positivo para `log(K/L)` y negativo para `log(K/L)^2`. Sin embargo, los errores estandar son grandes y el R2 es bajo. Por tanto, este resultado solo se interpreta como evidencia exploratoria, no como prueba causal.

## 7. Limitaciones

La principal limitacion tecnica fue que algunas fuentes no pudieron descargarse automaticamente. Esto se corrigio parcialmente construyendo D11 y D12 desde CSVs locales y cargando manualmente el PDF D6. Tambien hubo una limitacion operativa: la API LLM fallo por falta de cuota, de modo que la generacion final quedo en modo local de respaldo.

En la seccion empirica, las limitaciones son aun mas importantes: el analisis es cross-country, no causal; la muestra de paises ricos con markdowns aun no esta completa; y falta discutir endogeneidad, comparabilidad entre fuentes y posibles outliers.

## 8. Conclusiones

El proyecto construye un sistema RAG funcional para recuperar literatura economica y documentacion tecnica sobre automatizacion, capital-trabajo y wage markdowns. La version corregida recupera las fuentes esperadas para markdowns, automatizacion, Penn World Table y OECD EPL. Los fallos iniciales fueron informativos: mostraron que la calidad de un RAG depende tanto del modelo como de la construccion del corpus.

El trabajo cumple tambien una funcion estrategica: deja una base organizada para un paper futuro sobre la relacion no lineal entre K/L y wage markdowns. La extension empirica preliminar muestra signos compatibles con la hipotesis, pero debe ampliarse y tratarse como investigacion futura.

## 9. Bibliografia

- Acemoglu, D., y Restrepo, P. Automation and New Tasks.
- Acemoglu, D., y Restrepo, P. Robots and Jobs: Evidence from US Labor Markets.
- Amodio et al. (2024). Table A.2: Wage Markdown Distribution Across Countries.
- Feenstra, R., Inklaar, R., y Timmer, M. (2015). The Next Generation of the Penn World Table.
- Oberfield, E., y Raval, D. Micro Data and Macro Technology.
- OECD. Indicators of Employment Protection.
- World Bank. World Development Indicators: GDP per capita, PPP.
