# Notas de datos

## Archivos recibidos

- `amodio_table_a2_wage_markdowns.csv`: tabla digitada desde Table A.2, con p25, p50 y p75 del wage markdown por pais.
- `2026-05-18T01-31_export.csv`: extraccion tipo Penn World Table con `cn`, `emp`, `pop` y `rgdpna`.
- `2026-05-18T01-38_export.csv`: extraccion tipo Penn World Table con `cn`, `emp`, `pl_i` y otras variables de precios relativos.
- `Rkna-emp.csv`: extraccion con `rkna` y `emp`.
- `API_NY.GDP.PCAP.PP.KD_DS2_en_csv_v2_1700.csv`: GDP per capita PPP constante desde World Development Indicators.
- `OECD.ELS.JAI,DSD_EPL@DF_EPL,+A..EPL_OV..VERSION4.csv`: indicador OECD de employment protection legislation. Este archivo no parece contener wage markdowns; puede servir como control institucional o contexto, pero no sustituye los markdowns de la literatura OECD.

## Construccion preliminar

- Variable dependiente: `p50`, wage markdown mediano por pais desde Amodio et al.
- Intensidad de capital: `K/L = cn / emp`, promedio 2006-2019.
- Control de desarrollo: GDP per capita PPP constante, promedio 2006-2019.
- Transformaciones: `log(p50)`, `log(K/L)`, `log(K/L)^2`, `log(GDPpc PPP)`.

## Cobertura actual

- Paises en tabla de Amodio: 82.
- Paises con K/L: 80.
- Paises con GDPpc PPP: 80.
- Paises con variables centrales completas: 79.

## Paises incompletos en la muestra preliminar

- Kosovo: falta K/L y GDPpc PPP en los archivos actuales.
- Timor-Leste: falta K/L.
- Yemen: falta GDPpc PPP para el promedio usado.

## Advertencia metodologica

Esta base preliminar sirve como extension exploratoria para el trabajo RAG. Todavia no debe presentarse como evidencia causal. Para el paper futuro falta resolver comparabilidad de markdowns entre fuentes, ampliar paises OECD con markdowns reales, revisar outliers, justificar ventana temporal y evaluar endogeneidad.

