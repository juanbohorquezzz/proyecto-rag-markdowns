# Guion de video - maximo 5 minutos

## Distribucion sugerida

### 0:00-0:40 - Introduccion y problema

**Juan:**  
Nuestro proyecto construye un sistema RAG para apoyar una investigacion economica sobre automatizacion, intensidad de capital y poder de negociacion laboral. La pregunta de fondo es como el ratio capital-trabajo, K/L, puede relacionarse con el wage markdown, que usamos como medida de poder de mercado laboral o menor poder de negociacion de los trabajadores.

### 0:40-1:25 - Por que RAG

**Samuel:**  
Un LLM generico puede fallar en este dominio porque puede confundir markdown con markup, inventar resultados o responder sin fuentes. Por eso usamos RAG: primero recuperamos fragmentos relevantes de documentos reales y luego el modelo genera una respuesta usando solo ese contexto. Asi la respuesta es trazable.

### 1:25-2:10 - Documentos y datos

**Juan:**  
Usamos documentos sobre wage markdowns, automatizacion por tareas, Penn World Table, World Bank WDI y OECD EPL. Tambien construimos una base preliminar con markdowns de Amodio et al., K/L calculado como `cn / emp` desde PWT, GDP per capita PPP desde WDI y el indice EPL de OECD para una posible extension institucional.

### 2:10-3:05 - Arquitectura RAG

**Samuel:**  
El pipeline tiene estas etapas: extraemos texto de PDFs y paginas oficiales, dividimos en chunks de 350 palabras con overlap de 70, generamos embeddings con un modelo encoder multilingual, guardamos los vectores en FAISS y recuperamos los top-K fragmentos mas relevantes. Luego un LLM genera la respuesta con instrucciones de no inventar y citar fuentes.

### 3:05-4:10 - Demo en vivo

**Juan:**  
Primera pregunta sugerida: Que es un wage markdown y como se relaciona con poder de negociacion laboral?

**Samuel:**  
Segunda pregunta sugerida: Como conecta la automatizacion por tareas con la sustitucion entre capital y trabajo?

Mostrar en pantalla:

- Pregunta.
- Fragmentos recuperados.
- Scores de similitud.
- Respuesta generada.
- Fuentes citadas.

### 4:10-4:45 - Caso de fallo

**Juan:**  
Tambien probamos una pregunta que el sistema no deberia responder de forma inventada: cual es el efecto causal exacto de aumentar K/L en 10% sobre el markdown de Colombia en 2024? Si el contexto no contiene esa estimacion, el sistema debe decir que no puede responder causalmente.

### 4:45-5:00 - Cierre

**Samuel:**  
La conclusion es que el RAG funciona como herramienta de investigacion: organiza literatura, reduce alucinaciones y deja trazabilidad. Ademas, queda como base para un paper futuro sobre una relacion no lineal entre K/L y wage markdowns.

