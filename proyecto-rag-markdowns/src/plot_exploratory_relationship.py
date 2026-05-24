from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "report" / "figures"


def scale(value: float, src_min: float, src_max: float, dst_min: float, dst_max: float) -> float:
    return dst_min + (value - src_min) * (dst_max - dst_min) / (src_max - src_min)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROCESSED / "empirical_cross_section_2006_2019.csv")
    df = df[df["has_empirical_core"]].copy()

    x = df["log_kl"].to_numpy()
    y = df["log_markdown_p50"].to_numpy()
    coefficients = np.polyfit(x, y, deg=2)
    grid = np.linspace(x.min(), x.max(), 200)
    fitted = np.polyval(coefficients, grid)

    width, height = 900, 580
    left, right, top, bottom = 90, 35, 55, 80
    plot_w = width - left - right
    plot_h = height - top - bottom
    xmin, xmax = float(x.min()), float(x.max())
    ymin, ymax = float(y.min()), float(y.max())
    ypad = (ymax - ymin) * 0.08
    ymin -= ypad
    ymax += ypad

    def sx(v: float) -> float:
        return scale(v, xmin, xmax, left, left + plot_w)

    def sy(v: float) -> float:
        return scale(v, ymin, ymax, top + plot_h, top)

    circles = "\n".join(
        f'<circle cx="{sx(xi):.2f}" cy="{sy(yi):.2f}" r="4.3" fill="#2f6f73" opacity="0.78" stroke="white" stroke-width="0.7" />'
        for xi, yi in zip(x, y)
    )
    path_points = " ".join(
        f'{"M" if i == 0 else "L"} {sx(xi):.2f} {sy(yi):.2f}'
        for i, (xi, yi) in enumerate(zip(grid, fitted))
    )

    x_ticks = np.linspace(xmin, xmax, 5)
    y_ticks = np.linspace(ymin, ymax, 5)
    grid_lines = []
    tick_labels = []
    for tick in x_ticks:
        px = sx(float(tick))
        grid_lines.append(f'<line x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{top + plot_h}" stroke="#d9dee2" stroke-width="1" />')
        tick_labels.append(f'<text x="{px:.2f}" y="{height - 48}" text-anchor="middle" font-size="13" fill="#333">{tick:.1f}</text>')
    for tick in y_ticks:
        py = sy(float(tick))
        grid_lines.append(f'<line x1="{left}" y1="{py:.2f}" x2="{left + plot_w}" y2="{py:.2f}" stroke="#d9dee2" stroke-width="1" />')
        tick_labels.append(f'<text x="{left - 12}" y="{py + 4:.2f}" text-anchor="end" font-size="13" fill="#333">{tick:.1f}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{width / 2}" y="28" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#1f2933">Relacion exploratoria entre K/L y wage markdown</text>
  <g font-family="Arial, sans-serif">
    {''.join(grid_lines)}
    <line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#1f2933" stroke-width="1.4"/>
    <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#1f2933" stroke-width="1.4"/>
    <path d="{path_points}" fill="none" stroke="#b23a48" stroke-width="3"/>
    {circles}
    {''.join(tick_labels)}
    <text x="{left + plot_w / 2}" y="{height - 16}" text-anchor="middle" font-size="15" fill="#1f2933">log(K/L), promedio 2006-2019</text>
    <text x="20" y="{top + plot_h / 2}" text-anchor="middle" font-size="15" fill="#1f2933" transform="rotate(-90 20 {top + plot_h / 2})">log(wage markdown mediano)</text>
    <text x="{left + plot_w - 6}" y="{top + 18}" text-anchor="end" font-size="13" fill="#555">Curva cuadratica descriptiva</text>
  </g>
</svg>
'''
    out = FIGURES / "kl_markdown_exploratory.svg"
    out.write_text(svg, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
