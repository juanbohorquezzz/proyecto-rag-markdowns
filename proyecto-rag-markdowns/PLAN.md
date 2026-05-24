# Proyecto RAG: Capital-trabajo, automatizacion y wage markdowns

## Objetivo del trabajo del curso

Construir un sistema RAG que ayude a investigar la relacion entre intensidad de capital, automatizacion por tareas y poder de negociacion laboral medido por wage markdowns. El sistema debe responder preguntas tecnicas usando documentos reales y trazables, evitando respuestas inventadas o afirmaciones no soportadas.

## Pregunta guia del RAG

Como puede un sistema RAG apoyar el analisis de la relacion entre capital-trabajo, automatizacion y poder de negociacion laboral en la literatura economica?

## Pregunta futura del paper

Como afecta el ratio capital-trabajo (K/L) al poder de negociacion de los trabajadores, medido por el wage markdown?

## Hipotesis futura del paper

Las tareas estan ordenadas por dificultad de automatizacion. Las firmas automatizan primero las tareas mas faciles. A medida que aumenta K/L, las tareas marginales restantes son mas dificiles de automatizar, por lo que la elasticidad efectiva de sustitucion capital-trabajo cae. Esto debilita la amenaza de sustitucion laboral y reduce el wage markdown.

Prediccion empirica futura: relacion no lineal entre K/L y markdown, con beta_1 > 0 y beta_2 < 0 en una especificacion cuadratica.

## Entregables del curso

- Notebook reproducible con pipeline RAG completo.
- Reporte PDF ejecutivo.
- Video de sustentacion de maximo 5 minutos.
- Carpeta con documentos reales o enlaces verificables.
- Al menos 5 preguntas evaluadas con fragmentos recuperados, scores, respuesta y analisis cualitativo.

## Pipeline tecnico

1. Recolectar al menos 8 documentos reales.
2. Extraer texto de PDFs/documentos.
3. Dividir texto en chunks con overlap.
4. Generar embeddings.
5. Guardar embeddings en FAISS o Chroma.
6. Recuperar top-K fragmentos ante una pregunta.
7. Generar respuesta con un LLM usando solo el contexto recuperado.
8. Mostrar fuentes y trazabilidad.
9. Evaluar 5 preguntas y un caso de fallo.

## Documentos candidatos

- Amodio et al. (2024): wage markdowns en paises de ingreso bajo/medio.
- Yeh, Macaluso y Hershbein: monopsonio y markdowns.
- Mertens: labor market power / markdowns.
- Diez et al. o IMF: markups, markdowns y poder de mercado.
- OECD Employment Outlook o reporte sobre monopsonio/labour market power.
- Acemoglu y Restrepo: automatizacion, tareas y desplazamiento laboral.
- Oberfield y Raval (2021): elasticidad de sustitucion capital-trabajo.
- Penn World Table 10.x: documentacion de variables como cn y emp.
- World Bank WDI: documentacion de GDP per capita PPP.

## Preguntas de evaluacion candidatas

1. Que es un wage markdown y como se relaciona con el poder de negociacion laboral?
2. Como conecta la automatizacion por tareas con la sustitucion entre capital y trabajo?
3. Que evidencia existe sobre wage markdowns en paises de ingreso bajo y medio?
4. Como se mide el ratio capital-trabajo usando Penn World Table?
5. Que limitaciones hay al comparar wage markdowns entre paises ricos y paises en desarrollo?
6. Caso de fallo: cual es el efecto causal exacto de aumentar K/L en 10% sobre el wage markdown de Colombia en 2024?

## Lo que falta definir con el grupo

- Nombres de integrantes: Juan Bohorquez y Samuel Peña.
- Fecha de entrega.
- Entorno: Google Colab.
- Generacion: se permite usar API de LLM.
- Repositorio de GitHub donde se subiran documentos y codigo.
- Lista final de documentos y PDFs disponibles.
- Se incluira una mini seccion empirica exploratoria con K/L, GDPpc y markdowns.

## Avance con datos empíricos

- Se creo `data/raw/amodio_table_a2_wage_markdowns.csv` con la Table A.2.
- Se copiaron los CSVs recibidos a `data/raw`.
- Se creo `src/build_empirical_dataset.py` para construir la muestra 2006-2019.
- Se creo `data/processed/empirical_cross_section_2006_2019.csv`.
- La muestra preliminar tiene 79 paises con markdown, K/L y GDPpc completos.
- Se creo `src/run_exploratory_regressions.py` con las tres especificaciones OLS preliminares.
- Se creo `report/figures/kl_markdown_exploratory.svg` como grafico descriptivo inicial.
