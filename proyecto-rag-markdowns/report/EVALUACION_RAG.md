# Evaluacion cualitativa del RAG

## Resumen tecnico

- Documentos descargados o construidos con texto util: 10 fuentes utiles. Ocho provienen de PDFs/HTML descargados o cargados manualmente y dos son documentos estructurados construidos desde CSVs locales.
- Documentos bloqueados por 403 o sin texto: OECD EPL web e IMF Global Market Power. El bloqueo de OECD EPL se compenso con el documento estructurado D12 construido desde el CSV; OECD Employment Outlook 2020 se incorporo manualmente como PDF en D6.
- Chunks generados: 1010.
- Tamano de chunk: 350 palabras.
- Overlap: 70 palabras.
- Modelo de embeddings: `intfloat/multilingual-e5-small`.
- Dimension de embeddings: 384.
- Longitud maxima del encoder: 512 tokens.
- Base vectorial: FAISS con 1010 vectores.
- Top-K usado: 5.
- Generacion: API LLM configurada, pero no disponible en la corrida por falta de cuota. Se uso modo local de respaldo con fragmentos recuperados, scores y reglas de respuesta por dominio.

## Evaluacion por pregunta

| Pregunta | Top docs recuperados | Score maximo | Evaluacion | Alucinacion | Trazabilidad |
|---|---:|---:|---|---|---|
| Que es un wage markdown y como se relaciona con el poder de negociacion laboral? | D11, D11, D11, D11, D7 | 1.835 | Buena. Recupera la tabla estructurada de Amodio y conecta el markdown con poder de mercado laboral/bargaining. | Baja: el modo local no inventa cifras fuera del contexto. | Alta: D11 contiene la tabla estructurada de markdowns. |
| Como conecta la automatizacion por tareas con la sustitucion entre capital y trabajo? | D7, D7, D7, D7, D7 | 1.514 | Buena. Recupera el documento teorico correcto de Acemoglu y Restrepo y fragmentos sobre tareas, automatizacion y elasticidad de sustitucion. | Baja. | Alta: fragmentos trazables a D7. |
| Que evidencia existe sobre wage markdowns en paises de ingreso bajo y medio? | D11, D11, D11, D11, D1 | 1.834 | Buena. Recupera la fuente correcta sobre distribuciones de markdown por pais. | Baja. | Alta: D11 contiene p25, p50, p75 y observaciones por pais. |
| Como se mide el ratio capital-trabajo usando Penn World Table? | D3, D3, D2, D3, D3 | 1.400 | Buena. Recupera guia PWT y paper metodologico de PWT. | Baja. | Alta: fuentes correctas D2 y D3. |
| Que es el indice OECD EPL y por que podria importar para la heterogeneidad institucional? | D12, D12, D6, D6, D6 | 1.713 | Buena. Recupera el documento estructurado OECD EPL y el PDF de OECD Employment Outlook 2020. | Baja. | Alta: D12 contiene definicion y valores EPL_OV; D6 aporta contexto institucional OECD. |
| Cual es el efecto causal exacto de aumentar K/L en 10% sobre el wage markdown de Colombia en 2024? | D11, D11, D11, D11, D3 | 1.819 | Buen caso de fallo. El sistema no afirma causalidad exacta y explica que no existe una estimacion causal para Colombia 2024 en el contexto. | Baja. | Media-alta: recupera markdowns y PWT, aunque no una estimacion causal. |

## Lectura general

El componente de recuperacion funciona tecnicamente: genera embeddings, indexa 1010 chunks y devuelve fragmentos con scores. Tras agregar D11, D12 y el PDF manual D6, las preguntas centrales recuperan las fuentes esperadas: markdowns recupera Amodio estructurado, EPL recupera el documento OECD EPL estructurado y el PDF de Employment Outlook, automatizacion recupera Acemoglu-Restrepo y PWT recupera la guia/paper de Penn World Table.

## Mejoras inmediatas

1. Usar una API con cuota o un generador local pequeno para reemplazar el modo local de respaldo.
2. Agregar una fuente teorica mas directa sobre definicion de wage markdown/monopsonio.
3. Descargar manualmente las fuentes OECD/IMF bloqueadas para evitar depender de paginas con 403.
