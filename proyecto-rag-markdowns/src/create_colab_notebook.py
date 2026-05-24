import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "proyecto_rag_markdowns_colab.ipynb"


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip().splitlines(True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip().splitlines(True),
    }


cells = [
    md(
        """
        # Sistema RAG para investigar capital-trabajo, automatizacion y wage markdowns

        **Integrantes:** Juan Bohorquez y Samuel Peña  
        **Curso:** Parcial 2 - Proyecto RAG  
        **Dominio:** Economia laboral, automatizacion, intensidad de capital y poder de negociacion.

        Este notebook construye un pipeline Retrieval-Augmented Generation (RAG) para consultar documentos reales sobre wage markdowns, automatizacion por tareas, Penn World Table, GDP per capita PPP y rigidez laboral. Tambien incluye una extension empirica exploratoria que prepara la futura pregunta de paper: como se relaciona el ratio capital-trabajo `K/L` con el wage markdown mediano por pais.
        """
    ),
    md(
        """
        ## 1. Planteamiento del problema

        Un LLM generico no es suficiente para este problema porque puede confundir conceptos tecnicos como markdown, markup, monopsonio, poder de negociacion, capital stock o elasticidad de sustitucion. Tambien puede inventar resultados empiricos o citar mal fuentes.

        El RAG es adecuado porque obliga al modelo a responder usando fragmentos recuperados desde documentos verificables. Esto reduce alucinaciones y deja trazabilidad: cada respuesta se puede conectar con documentos concretos.

        La pregunta futura del paper es:

        > Como afecta el ratio capital-trabajo (K/L) al poder de negociacion de los trabajadores, medido por el wage markdown?

        Para el curso, el objetivo es construir el asistente RAG que permita revisar, recuperar y sintetizar la literatura y documentacion necesaria para esa investigacion.
        """
    ),
    code(
        """
        !pip -q install pandas numpy pypdf sentence-transformers faiss-cpu openai requests tqdm beautifulsoup4 matplotlib scikit-learn
        """
    ),
    code(
        """
        import os
        import re
        import math
        import json
        import textwrap
        from pathlib import Path
        from typing import Dict, List

        import faiss
        import numpy as np
        import pandas as pd
        import requests
        from bs4 import BeautifulSoup
        from pypdf import PdfReader
        from sentence_transformers import SentenceTransformer
        from tqdm.auto import tqdm

        import matplotlib.pyplot as plt

        try:
            from google.colab import userdata
        except Exception:
            userdata = None
        """
    ),
    md(
        """
        ## 2. Configuracion

        En Google Colab, suban la carpeta del proyecto o clonen el repositorio. La carpeta debe contener `data/raw`, `requirements_colab.txt` y este notebook.

        Para usar la API, guarden la clave como secret de Colab con el nombre `OPENAI_API_KEY`, o definan la variable de entorno manualmente.
        """
    ),
    code(
        """
        # Ajuste automatico de ruta:
        # 1. Si el notebook esta dentro de la carpeta notebooks, subimos un nivel.
        # 2. Si Colab clono/subio una carpeta llamada proyecto-rag-markdowns, la usamos.
        # 3. Si ya estamos en la raiz del proyecto, usamos la carpeta actual.
        candidates = [
            Path.cwd(),
            Path.cwd().parent,
            Path("/content/proyecto-rag-markdowns"),
            Path("/content/drive/MyDrive/proyecto-rag-markdowns"),
        ]
        PROJECT_DIR = None
        for candidate in candidates:
            if (candidate / "data" / "raw").exists():
                PROJECT_DIR = candidate
                break
        if PROJECT_DIR is None:
            PROJECT_DIR = Path.cwd()

        RAW_DIR = PROJECT_DIR / "data" / "raw"
        DOC_DIR = RAW_DIR / "documents"
        PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
        FIGURES_DIR = PROJECT_DIR / "report" / "figures"

        for path in [RAW_DIR, DOC_DIR, PROCESSED_DIR, FIGURES_DIR]:
            path.mkdir(parents=True, exist_ok=True)

        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        if OPENAI_API_KEY is None and userdata is not None:
            try:
                OPENAI_API_KEY = userdata.get("OPENAI_API_KEY")
            except Exception:
                OPENAI_API_KEY = None

        OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")
        print("Proyecto:", PROJECT_DIR)
        print("API configurada:", OPENAI_API_KEY is not None)
        """
    ),
    md(
        """
        ## 3. Documentos del RAG

        El proyecto usa documentos reales. Algunos son PDFs y otros son paginas HTML oficiales. Si una descarga falla en Colab, descarguen manualmente el documento y subanlo a `data/raw/documents`.
        """
    ),
    code(
        """
        DOCUMENTS = [
            {
                "doc_id": "D1",
                "title": "Amodio et al. (2024) - Wage markdowns, appendix Table A.2",
                "url": "https://www.econstor.eu/bitstream/10419/295719/1/cream-dp2404.pdf",
                "filename": "amodio_2024_wage_markdowns.pdf",
                "role": "Fuente central de markdowns por pais.",
            },
            {
                "doc_id": "D2",
                "title": "PWT 10.0 User Guide",
                "url": "https://www.rug.nl/ggdc/docs/pwt100-user-guide-to-data-files.pdf",
                "filename": "pwt100_user_guide.pdf",
                "role": "Definicion de variables PWT y advertencias de uso.",
            },
            {
                "doc_id": "D3",
                "title": "Feenstra, Inklaar and Timmer (2015) - The Next Generation of PWT",
                "url": "https://www.rug.nl/ggdc/docs/the_next_generation_of_the_penn_world_table.pdf",
                "filename": "feenstra_inklaar_timmer_2015_pwt.pdf",
                "role": "Fundamento metodologico de Penn World Table.",
            },
            {
                "doc_id": "D4",
                "title": "World Bank WDI - GDP per capita PPP constant 2021 international dollars",
                "url": "https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD",
                "filename": "world_bank_gdppc_ppp.html",
                "role": "Metadatos del indicador GDPpc PPP.",
            },
            {
                "doc_id": "D5",
                "title": "OECD Indicators of Employment Protection",
                "url": "https://www.oecd.org/en/data/datasets/oecd-indicators-of-employment-protection.html",
                "filename": "oecd_epl_indicators.html",
                "role": "Fuente del indice EPL.",
            },
            {
                "doc_id": "D6",
                "title": "OECD Employment Outlook 2020 - Recent trends in EPL",
                "url": "https://www.oecd.org/en/publications/oecd-employment-outlook-2020_1686c758-en/full-report/component-8.html",
                "filename": "oecd_employment_outlook_2020_epl.html",
                "role": "Metodologia y revision de EPL version 4.",
            },
            {
                "doc_id": "D7",
                "title": "Acemoglu and Restrepo (2019) - Automation and New Tasks",
                "url": "https://economics.mit.edu/sites/default/files/publications/Automation%20and%20New%20Tasks%20-%20How%20Technology%20Displace.pdf",
                "filename": "acemoglu_restrepo_2019_automation_new_tasks.pdf",
                "role": "Marco teorico de automatizacion por tareas.",
            },
            {
                "doc_id": "D8",
                "title": "Acemoglu and Restrepo - Robots and Jobs",
                "url": "https://economics.mit.edu/sites/default/files/publications/Robots%20and%20Jobs%20-%20Evidence%20from%20US%20Labor%20Markets.p.pdf",
                "filename": "acemoglu_restrepo_robots_jobs.pdf",
                "role": "Evidencia sobre robots, empleo y salarios.",
            },
            {
                "doc_id": "D9",
                "title": "Oberfield and Raval - Micro Data and Macro Technology",
                "url": "https://economics.sas.upenn.edu/sites/default/files/filevault/u21/Oberfield_Raval.pdf",
                "filename": "oberfield_raval_micro_data_macro_technology.pdf",
                "role": "Elasticidad de sustitucion capital-trabajo.",
            },
            {
                "doc_id": "D10",
                "title": "Diez, Leigh and Tambunlertchai (2018) - Global Market Power",
                "url": "https://www.imf.org/~/media/Files/Publications/WP/2018/wp18137.ashx",
                "filename": "diez_leigh_tambunlertchai_2018_global_market_power.pdf",
                "role": "Poder de mercado, inversion y labor share.",
            },
        ]

        pd.DataFrame(DOCUMENTS)
        """
    ),
    code(
        """
        def download_file(url: str, target: Path) -> bool:
            if target.exists() and target.stat().st_size > 1000:
                return True
            try:
                response = requests.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                target.write_bytes(response.content)
                return True
            except Exception as exc:
                print(f"No se pudo descargar {url}: {exc}")
                return False

        for doc in DOCUMENTS:
            ok = download_file(doc["url"], DOC_DIR / doc["filename"])
            print(doc["doc_id"], ok, doc["filename"])
        """
    ),
    md(
        """
        ## 4. Extraccion de texto

        Extraemos texto de PDFs con `pypdf` y de HTML con `BeautifulSoup`. Cada documento mantiene metadatos para que las respuestas sean trazables.
        """
    ),
    code(
        """
        def clean_text(text: str) -> str:
            text = re.sub(r"\\s+", " ", text)
            return text.strip()

        def extract_pdf(path: Path) -> str:
            reader = PdfReader(str(path))
            pages = []
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                except Exception:
                    page_text = ""
                pages.append(f"\\n[page {i+1}]\\n{page_text}")
            return clean_text("\\n".join(pages))

        def extract_html(path: Path) -> str:
            soup = BeautifulSoup(path.read_text(errors="ignore"), "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            return clean_text(soup.get_text(" "))

        def extract_document_text(doc: dict) -> dict:
            path = DOC_DIR / doc["filename"]
            if not path.exists():
                return {**doc, "text": "", "chars": 0}
            if path.suffix.lower() == ".pdf":
                text = extract_pdf(path)
            else:
                text = extract_html(path)
            return {**doc, "text": text, "chars": len(text)}

        documents = [extract_document_text(doc) for doc in DOCUMENTS]
        doc_df = pd.DataFrame([{k: v for k, v in d.items() if k != "text"} for d in documents])
        doc_df
        """
    ),
    md(
        """
        ## 5. Chunking

        Usamos chunks de 350 palabras con overlap de 70 palabras. La idea es que cada fragmento sea suficientemente corto para embeddings precisos, pero suficientemente largo para conservar contexto economico. Si los chunks son muy pequeños, se pierde argumento; si son muy grandes, baja la precision de recuperacion.
        """
    ),
    code(
        """
        CHUNK_WORDS = 350
        OVERLAP_WORDS = 70

        def chunk_text(text: str, chunk_words: int = CHUNK_WORDS, overlap_words: int = OVERLAP_WORDS) -> List[str]:
            words = text.split()
            chunks = []
            step = chunk_words - overlap_words
            for start in range(0, len(words), step):
                piece = words[start:start + chunk_words]
                if len(piece) < 80:
                    continue
                chunks.append(" ".join(piece))
            return chunks

        chunks = []
        for doc in documents:
            for idx, chunk in enumerate(chunk_text(doc["text"])):
                chunks.append({
                    "chunk_id": f'{doc["doc_id"]}_{idx:04d}',
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "source_url": doc["url"],
                    "chunk_index": idx,
                    "text": chunk,
                    "word_count": len(chunk.split()),
                })

        chunks_df = pd.DataFrame(chunks)
        chunks_df.to_csv(PROCESSED_DIR / "rag_chunks.csv", index=False)

        print("Documentos con texto:", sum(d["chars"] > 0 for d in documents))
        print("Chunks generados:", len(chunks_df))
        chunks_df["word_count"].describe()
        """
    ),
    code(
        """
        plt.figure(figsize=(7, 4))
        chunks_df["word_count"].hist(bins=25, color="#2f6f73")
        plt.title("Distribucion de tamanos de chunks")
        plt.xlabel("Palabras por chunk")
        plt.ylabel("Frecuencia")
        plt.tight_layout()
        plt.show()
        """
    ),
    md(
        """
        ## 6. Embeddings y base vectorial

        Usamos `intfloat/multilingual-e5-small`, un modelo encoder multilingual. Convierte textos y preguntas en vectores comparables. La busqueda se hace con FAISS usando producto interno sobre vectores normalizados, equivalente a similitud coseno.
        """
    ),
    code(
        """
        EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-small"
        encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Modelo encoder:", EMBEDDING_MODEL_NAME)
        print("Dimension:", encoder.get_sentence_embedding_dimension())
        print("Max sequence length:", encoder.max_seq_length)

        passage_texts = ["passage: " + t for t in chunks_df["text"].tolist()]
        embeddings = encoder.encode(
            passage_texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True,
        ).astype("float32")

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        print("Vectores indexados:", index.ntotal)
        """
    ),
    md(
        """
        ## 7. Recuperacion top-K

        Para cada pregunta, convertimos el query en embedding y recuperamos los `K` fragmentos mas similares. Usamos `K=5` como punto de partida: suficiente para cubrir varias fuentes, sin saturar el prompt.
        """
    ),
    code(
        """
        TOP_K = 5

        def retrieve(query: str, top_k: int = TOP_K) -> pd.DataFrame:
            q_emb = encoder.encode(
                ["query: " + query],
                normalize_embeddings=True,
            ).astype("float32")
            scores, ids = index.search(q_emb, top_k)
            rows = chunks_df.iloc[ids[0]].copy()
            rows["score"] = scores[0]
            return rows[["chunk_id", "doc_id", "title", "score", "text", "source_url"]]

        test_query = "Que es un wage markdown y como mide poder de mercado laboral?"
        retrieve(test_query)
        """
    ),
    md(
        """
        ## 8. Generacion con LLM

        El modelo generador recibe solo la pregunta y los fragmentos recuperados. El prompt le exige responder con cautela, citar fuentes por `doc_id` y admitir cuando el contexto no permite responder.
        """
    ),
    code(
        """
        from openai import OpenAI

        if OPENAI_API_KEY:
            client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            client = None

        SYSTEM_PROMPT = '''
        Eres un asistente de investigacion economica. Responde en espanol.
        Usa exclusivamente el contexto recuperado. No inventes resultados, autores, cifras ni causalidad.
        Si el contexto no permite responder, dilo claramente y explica que informacion faltaria.
        Cita las fuentes usando el formato [D1], [D2], etc.
        Distingue entre evidencia documentada, interpretacion y extension hipotetica.
        '''.strip()

        def build_context(retrieved: pd.DataFrame) -> str:
            blocks = []
            for _, row in retrieved.iterrows():
                blocks.append(
                    f'[{row.doc_id}] {row.title}\\nScore: {row.score:.3f}\\nFragmento: {row.text}'
                )
            return "\\n\\n---\\n\\n".join(blocks)

        def answer_question(question: str, top_k: int = TOP_K) -> Dict:
            retrieved = retrieve(question, top_k=top_k)
            context = build_context(retrieved)
            prompt = f'''
            Pregunta del usuario:
            {question}

            Contexto recuperado:
            {context}

            Responde con:
            1. Respuesta breve y directa.
            2. Evidencia usada, con citas [D#].
            3. Cautelas o limitaciones.
            '''.strip()

            if client is None:
                answer = "API no configurada. Configure OPENAI_API_KEY para generar respuesta."
            else:
                response = client.responses.create(
                    model=OPENAI_MODEL,
                    instructions=SYSTEM_PROMPT,
                    input=prompt,
                )
                answer = response.output_text
            return {"question": question, "retrieved": retrieved, "answer": answer}
        """
    ),
    md(
        """
        ## 9. Evaluacion cualitativa

        Probamos al menos 5 preguntas representativas y un caso de fallo. Para cada una se reportan fragmentos, scores, respuesta y evaluacion cualitativa.
        """
    ),
    code(
        """
        QUESTIONS = [
            "Que es un wage markdown y como se relaciona con el poder de negociacion laboral?",
            "Como conecta la automatizacion por tareas con la sustitucion entre capital y trabajo?",
            "Que evidencia existe sobre wage markdowns en paises de ingreso bajo y medio?",
            "Como se mide el ratio capital-trabajo usando Penn World Table?",
            "Que es el indice OECD EPL y por que podria importar para la heterogeneidad institucional?",
            "Cual es el efecto causal exacto de aumentar K/L en 10% sobre el wage markdown de Colombia en 2024?",
        ]

        results = []
        for q in QUESTIONS:
            print("=" * 100)
            print("PREGUNTA:", q)
            result = answer_question(q, top_k=5)
            print("\\nFRAGMENTOS RECUPERADOS")
            display(result["retrieved"][["doc_id", "title", "score"]])
            print("\\nRESPUESTA")
            print(result["answer"])
            results.append(result)
        """
    ),
    code(
        """
        evaluation_rows = []
        for result in results:
            evaluation_rows.append({
                "question": result["question"],
                "top_docs": ", ".join(result["retrieved"]["doc_id"].tolist()),
                "max_score": float(result["retrieved"]["score"].max()),
                "qualitative_assessment": "",
                "hallucination_check": "",
                "traceability_check": "",
            })

        evaluation_df = pd.DataFrame(evaluation_rows)
        evaluation_df.to_csv(PROCESSED_DIR / "rag_evaluation_template.csv", index=False)
        evaluation_df
        """
    ),
    md(
        """
        ## 10. Extension empirica exploratoria

        Esta seccion no es la prueba causal del paper. Sirve para mostrar como los datos actuales motivan la hipotesis futura.

        Construimos:

        - `markdown`: p50 de Amodio et al.
        - `K/L`: `cn / emp` desde PWT, promedio 2006-2019.
        - `GDPpc`: GDP per capita PPP constante desde WDI, promedio 2006-2019.
        """
    ),
    code(
        """
        YEARS = [str(y) for y in range(2006, 2020)]

        markdown_path = RAW_DIR / "amodio_table_a2_wage_markdowns.csv"
        pwt_path = RAW_DIR / "2026-05-18T01-31_export.csv"
        wdi_path = RAW_DIR / "API_NY.GDP.PCAP.PP.KD_DS2_en_csv_v2_1700.csv"

        markdowns = pd.read_csv(markdown_path)
        pwt = pd.read_csv(pwt_path, encoding="utf-8-sig")
        wdi = pd.read_csv(wdi_path, encoding="utf-8-sig", skiprows=4)

        wanted = pwt[pwt["Variable code"].isin(["cn", "emp"])].copy()
        long = wanted.melt(
            id_vars=["ISO code", "Country", "Variable code", "Variable name"],
            value_vars=YEARS,
            var_name="year",
            value_name="value",
        )
        long["value"] = pd.to_numeric(long["value"], errors="coerce")
        wide = long.pivot_table(
            index=["ISO code", "Country", "year"],
            columns="Variable code",
            values="value",
            aggfunc="first",
        ).reset_index()
        wide["kl_cn_emp"] = wide["cn"] / wide["emp"]
        kl = (
            wide.groupby(["ISO code", "Country"], as_index=False)
            .agg(kl_2006_2019=("kl_cn_emp", "mean"), kl_years_available=("kl_cn_emp", "count"))
            .rename(columns={"ISO code": "country_code", "Country": "country_name_pwt"})
        )

        wdi_small = wdi[["Country Name", "Country Code"] + YEARS].copy()
        for year in YEARS:
            wdi_small[year] = pd.to_numeric(wdi_small[year], errors="coerce")
        wdi_small["gdppc_ppp_2006_2019"] = wdi_small[YEARS].mean(axis=1, skipna=True)
        gdppc = wdi_small.rename(columns={"Country Code": "country_code", "Country Name": "country_name_wdi"})[
            ["country_code", "country_name_wdi", "gdppc_ppp_2006_2019"]
        ]

        empirical = markdowns.merge(kl, on="country_code", how="left").merge(gdppc, on="country_code", how="left")
        empirical["log_markdown_p50"] = np.log(empirical["p50"])
        empirical["log_kl"] = np.log(empirical["kl_2006_2019"])
        empirical["log_kl_sq"] = empirical["log_kl"] ** 2
        empirical["log_gdppc_ppp"] = np.log(empirical["gdppc_ppp_2006_2019"])
        empirical["has_core"] = empirical[["log_markdown_p50", "log_kl", "log_gdppc_ppp"]].notna().all(axis=1)

        empirical.to_csv(PROCESSED_DIR / "empirical_cross_section_2006_2019.csv", index=False)
        empirical["has_core"].value_counts()
        """
    ),
    code(
        """
        df = empirical[empirical["has_core"]].copy()

        def fit_ols(y, X, names):
            X = np.asarray(X)
            y = np.asarray(y)
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            resid = y - X @ beta
            n, k = X.shape
            sse = float(resid.T @ resid)
            tss = float(((y - y.mean()) ** 2).sum())
            sigma2 = sse / (n - k)
            vcov = sigma2 * np.linalg.inv(X.T @ X)
            se = np.sqrt(np.diag(vcov))
            return pd.DataFrame({
                "term": names,
                "estimate": beta,
                "std_error": se,
                "t_stat": beta / se,
                "n": n,
                "r2": 1 - sse / tss,
            })

        y = df["log_markdown_p50"].to_numpy()
        specs = []

        X1 = np.column_stack([np.ones(len(df)), df["log_kl"]])
        specs.append(("M1", fit_ols(y, X1, ["intercept", "log_kl"])))

        X2 = np.column_stack([np.ones(len(df)), df["log_kl"], df["log_gdppc_ppp"]])
        specs.append(("M2", fit_ols(y, X2, ["intercept", "log_kl", "log_gdppc_ppp"])))

        X3 = np.column_stack([np.ones(len(df)), df["log_kl"], df["log_kl_sq"], df["log_gdppc_ppp"]])
        specs.append(("M3", fit_ols(y, X3, ["intercept", "log_kl", "log_kl_sq", "log_gdppc_ppp"])))

        reg_results = pd.concat([table.assign(spec=name) for name, table in specs], ignore_index=True)
        reg_results.to_csv(PROCESSED_DIR / "ols_exploratory_results.csv", index=False)
        reg_results
        """
    ),
    code(
        """
        x = df["log_kl"]
        y = df["log_markdown_p50"]
        coeff = np.polyfit(x, y, deg=2)
        grid = np.linspace(x.min(), x.max(), 200)
        fitted = np.polyval(coeff, grid)

        plt.figure(figsize=(8, 5))
        plt.scatter(x, y, alpha=0.75, color="#2f6f73", edgecolor="white")
        plt.plot(grid, fitted, color="#b23a48", linewidth=2.5)
        plt.title("Relacion exploratoria entre K/L y wage markdown")
        plt.xlabel("log(K/L), promedio 2006-2019")
        plt.ylabel("log(wage markdown mediano)")
        plt.grid(alpha=0.25)
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "kl_markdown_exploratory_colab.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        ## 11. Conclusiones preliminares para el reporte

        - El sistema RAG permite responder preguntas tecnicas con trazabilidad documental.
        - La base empirica preliminar permite conectar el trabajo del curso con el futuro paper.
        - El resultado empirico no debe presentarse como causal: por ahora solo motiva la hipotesis.
        - Falta incorporar una fuente confiable de wage markdowns para paises ricos si se quiere ampliar la muestra mas alla de Amodio.
        - El caso de fallo debe mostrar que el sistema no puede inferir un efecto causal exacto para Colombia 2024 si esa informacion no esta en los documentos.
        """
    ),
]


notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": []},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
NOTEBOOK.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
print(NOTEBOOK)
