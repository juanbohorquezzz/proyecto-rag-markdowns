# Inventario inicial de fuentes

Este inventario separa fuentes de datos y documentos candidatos para el RAG. La lista puede crecer cuando el grupo agregue PDFs adicionales.

## Fuentes de datos ya incorporadas

| Fuente | Uso en el proyecto | Archivo local |
|---|---|---|
| Amodio et al. (2024), Table A.2 | Wage markdown p25, p50 y p75 por pais | `data/raw/amodio_table_a2_wage_markdowns.csv` |
| Penn World Table | `cn`, `emp`, `pop`, `pl_i`, `pl_gdpo`; construccion de `K/L = cn / emp` | `data/raw/2026-05-18T01-31_export.csv`, `data/raw/2026-05-18T01-38_export.csv`, `data/raw/Rkna-emp.csv` |
| World Bank WDI | GDP per capita PPP constante | `data/raw/API_NY.GDP.PCAP.PP.KD_DS2_en_csv_v2_1700.csv` |
| OECD EPL | Rigidez/proteccion laboral por pais | `data/raw/OECD.ELS.JAI,DSD_EPL@DF_EPL,+A..EPL_OV..VERSION4.csv` |

## Documentos candidatos para el RAG

| ID | Documento | Rol en el RAG | URL |
|---|---|---|---|
| D1 | Amodio et al. (2024), apendice con Table A.2 | Fuente central de wage markdowns en paises de ingreso bajo/medio | https://www.econstor.eu/bitstream/10419/295719/1/cream-dp2404.pdf |
| D2 | Penn World Table 10.0 User Guide | Definicion y advertencias de variables PWT | https://www.rug.nl/ggdc/docs/pwt100-user-guide-to-data-files.pdf |
| D3 | Feenstra, Inklaar y Timmer (2015), The Next Generation of the Penn World Table | Fundamento metodologico de PWT | https://www.rug.nl/ggdc/docs/the_next_generation_of_the_penn_world_table.pdf |
| D4 | World Bank WDI: GDP per capita PPP constant 2021 international dollars | Definicion y metadatos de GDPpc PPP | https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD |
| D5 | OECD Indicators of Employment Protection | Fuente del indice EPL | https://www.oecd.org/en/data/datasets/oecd-indicators-of-employment-protection.html |
| D6 | OECD Employment Outlook 2020, chapter on EPL | Documentacion de EPL version 4 y metodologia | https://www.oecd.org/en/publications/oecd-employment-outlook-2020_1686c758-en/full-report/component-8.html |
| D7 | Acemoglu y Restrepo (2019), Automation and New Tasks | Marco teorico de automatizacion por tareas | https://economics.mit.edu/sites/default/files/publications/Automation%20and%20New%20Tasks%20-%20How%20Technology%20Displace.pdf |
| D8 | Acemoglu y Restrepo, Robots and Jobs | Evidencia sobre robots, tareas, empleo y salarios | https://economics.mit.edu/sites/default/files/publications/Robots%20and%20Jobs%20-%20Evidence%20from%20US%20Labor%20Markets.p.pdf |
| D9 | Oberfield y Raval, Micro Data and Macro Technology | Elasticidad de sustitucion capital-trabajo | https://economics.sas.upenn.edu/sites/default/files/filevault/u21/Oberfield_Raval.pdf |
| D10 | Diez, Leigh y Tambunlertchai (2018), Global Market Power and its Macroeconomic Implications | Poder de mercado y relacion con inversion/labor share | https://www.imf.org/~/media/Files/Publications/WP/2018/wp18137.ashx |

## Fuente pendiente

Falta localizar o aportar una fuente tabular clara de wage markdowns para paises ricos/OECD. El archivo OECD EPL no contiene markdowns; contiene regulacion laboral. Para el paper futuro, esta pieza sera necesaria si se quiere llegar a la muestra ampliada de 92 paises.

