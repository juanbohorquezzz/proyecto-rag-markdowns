from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def fit_ols(y: np.ndarray, x: np.ndarray) -> dict:
    n, k = x.shape
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    resid = y - x @ beta
    sse = float(resid.T @ resid)
    tss = float(((y - y.mean()) ** 2).sum())
    sigma2 = sse / (n - k)
    xtx_inv = np.linalg.inv(x.T @ x)
    se = np.sqrt(np.diag(sigma2 * xtx_inv))
    tstat = beta / se
    r2 = 1 - sse / tss
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k)
    return {
        "n": n,
        "k": k,
        "beta": beta,
        "se": se,
        "tstat": tstat,
        "r2": r2,
        "adj_r2": adj_r2,
    }


def main() -> None:
    df = pd.read_csv(PROCESSED / "empirical_cross_section_2006_2019.csv")
    df = df[df["has_empirical_core"]].copy()

    specs = {
        "M1_log_kl": ["log_kl"],
        "M2_log_kl_log_gdppc": ["log_kl", "log_gdppc_ppp"],
        "M3_quadratic_log_kl_log_gdppc": ["log_kl", "log_kl_sq", "log_gdppc_ppp"],
    }

    rows = []
    y = df["log_markdown_p50"].to_numpy()
    for spec_name, variables in specs.items():
        x = np.column_stack([np.ones(len(df))] + [df[var].to_numpy() for var in variables])
        result = fit_ols(y, x)
        names = ["intercept"] + variables
        for name, beta, se, tstat in zip(
            names, result["beta"], result["se"], result["tstat"]
        ):
            rows.append(
                {
                    "spec": spec_name,
                    "term": name,
                    "estimate": beta,
                    "std_error": se,
                    "t_stat": tstat,
                    "n": result["n"],
                    "r2": result["r2"],
                    "adj_r2": result["adj_r2"],
                }
            )

    out = pd.DataFrame(rows)
    out.to_csv(PROCESSED / "ols_exploratory_results.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
