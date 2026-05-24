from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
YEARS = [str(year) for year in range(2006, 2020)]


def read_pwt_wide(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def build_kl(pwt: pd.DataFrame) -> pd.DataFrame:
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
    wide["year"] = wide["year"].astype(int)

    return (
        wide.groupby(["ISO code", "Country"], as_index=False)
        .agg(
            kl_2006_2019=("kl_cn_emp", "mean"),
            kl_years_available=("kl_cn_emp", "count"),
            cn_2006_2019=("cn", "mean"),
            emp_2006_2019=("emp", "mean"),
        )
        .rename(columns={"ISO code": "country_code", "Country": "country_name_pwt"})
    )


def build_gdppc(wdi_path: Path) -> pd.DataFrame:
    wdi = pd.read_csv(wdi_path, encoding="utf-8-sig", skiprows=4)
    wdi_years = ["Country Name", "Country Code"] + YEARS
    wdi = wdi[wdi_years].copy()
    for year in YEARS:
        wdi[year] = pd.to_numeric(wdi[year], errors="coerce")
    wdi["gdppc_ppp_2006_2019"] = wdi[YEARS].mean(axis=1, skipna=True)
    wdi["gdppc_years_available"] = wdi[YEARS].notna().sum(axis=1)
    return wdi.rename(
        columns={
            "Country Code": "country_code",
            "Country Name": "country_name_wdi",
        }
    )[["country_code", "country_name_wdi", "gdppc_ppp_2006_2019", "gdppc_years_available"]]


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    markdowns = pd.read_csv(RAW / "amodio_table_a2_wage_markdowns.csv")
    pwt = read_pwt_wide(RAW / "2026-05-18T01-31_export.csv")
    kl = build_kl(pwt)
    gdppc = build_gdppc(RAW / "API_NY.GDP.PCAP.PP.KD_DS2_en_csv_v2_1700.csv")

    merged = (
        markdowns.merge(kl, on="country_code", how="left")
        .merge(gdppc, on="country_code", how="left")
    )
    merged["log_markdown_p50"] = np.log(merged["p50"])
    merged["log_kl"] = np.log(merged["kl_2006_2019"])
    merged["log_kl_sq"] = merged["log_kl"] ** 2
    merged["log_gdppc_ppp"] = np.log(merged["gdppc_ppp_2006_2019"])
    merged["has_empirical_core"] = merged[
        ["log_markdown_p50", "log_kl", "log_gdppc_ppp"]
    ].notna().all(axis=1)

    merged.to_csv(PROCESSED / "empirical_cross_section_2006_2019.csv", index=False)

    summary = pd.DataFrame(
        [
            {"metric": "countries_in_amodio_table", "value": len(markdowns)},
            {"metric": "countries_with_kl", "value": int(merged["kl_2006_2019"].notna().sum())},
            {
                "metric": "countries_with_gdppc",
                "value": int(merged["gdppc_ppp_2006_2019"].notna().sum()),
            },
            {
                "metric": "countries_with_core_regression_variables",
                "value": int(merged["has_empirical_core"].sum()),
            },
        ]
    )
    summary.to_csv(PROCESSED / "empirical_dataset_summary.csv", index=False)

    missing = merged.loc[
        ~merged["has_empirical_core"],
        ["country_code", "country_name", "kl_2006_2019", "gdppc_ppp_2006_2019"],
    ]
    missing.to_csv(PROCESSED / "empirical_missing_core_variables.csv", index=False)

    print(summary.to_string(index=False))
    if not missing.empty:
        print("\nMissing core variables:")
        print(missing.to_string(index=False))


if __name__ == "__main__":
    main()
