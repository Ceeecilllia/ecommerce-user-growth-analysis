from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter, PercentFormatter


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUTPUT = ROOT / "dashboard"
TABLEAU = OUTPUT / "tableau_data"
OUTPUT.mkdir(exist_ok=True)
TABLEAU.mkdir(exist_ok=True)

BLUE = "#2563EB"
DARK_BLUE = "#1E3A8A"
LIGHT_BLUE = "#DBEAFE"
AMBER = "#F59E0B"
DARK = "#172033"
MUTED = "#667085"
GRID = "#E4E7EC"
BG = "#F7F9FC"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(
        DATA / "online_retail_clean.csv.gz",
        compression="gzip",
        parse_dates=["InvoiceDate"],
        dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": str},
    )
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M")
    return df


def build_sources(df: pd.DataFrame):
    order_level = (
        df.groupby("InvoiceNo", as_index=False)
        .agg(CustomerID=("CustomerID", "first"), OrderRevenue=("Revenue", "sum"))
    )
    customer_orders = order_level.groupby("CustomerID")["InvoiceNo"].nunique()
    repeat_customers = int((customer_orders >= 2).sum())

    kpis = pd.DataFrame(
        {
            "Metric": ["Revenue", "Orders", "Customers", "AOV", "Repeat Customer Rate"],
            "Value": [
                df["Revenue"].sum(),
                df["InvoiceNo"].nunique(),
                df["CustomerID"].nunique(),
                df["Revenue"].sum() / df["InvoiceNo"].nunique(),
                repeat_customers / df["CustomerID"].nunique(),
            ],
        }
    )

    monthly = pd.read_csv(DATA / "monthly_kpis.csv")
    monthly["InvoiceMonth"] = monthly["InvoiceMonth"].astype(str)

    first_month = df.groupby("CustomerID")["InvoiceMonth"].min()
    df["FirstPurchaseMonth"] = df["CustomerID"].map(first_month)
    df["CustomerType"] = np.where(
        df["InvoiceMonth"] == df["FirstPurchaseMonth"], "New", "Returning"
    )
    customer_type = (
        df.groupby(["InvoiceMonth", "CustomerType"])["Revenue"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    customer_type["InvoiceMonth"] = customer_type["InvoiceMonth"].astype(str)

    country = pd.read_csv(DATA / "country_summary.csv")
    country = country[country["Country"] != "United Kingdom"].head(10)

    rfm = pd.read_csv(DATA / "rfm_segment_summary.csv")
    cohort = pd.read_csv(DATA / "monthly_cohort_retention.csv", index_col=0)
    cohort.index = cohort.index.astype(str)
    cohort_long = (
        cohort.reset_index(names="CohortMonth")
        .melt(id_vars="CohortMonth", var_name="CohortIndex", value_name="RetentionRate")
        .dropna(subset=["RetentionRate"])
    )

    kpis.to_csv(TABLEAU / "kpi_summary.csv", index=False)
    monthly.to_csv(TABLEAU / "monthly_performance.csv", index=False)
    customer_type.to_csv(TABLEAU / "new_returning_revenue.csv", index=False)
    country.to_csv(TABLEAU / "international_markets.csv", index=False)
    rfm.to_csv(TABLEAU / "rfm_segment_summary.csv", index=False)
    cohort_long.to_csv(TABLEAU / "cohort_retention_long.csv", index=False)
    return kpis, monthly, customer_type, country, rfm, cohort


def style_axis(ax):
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def add_card(fig, x, y, w, h, title, value, note=None):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.006,rounding_size=0.012",
        transform=fig.transFigure,
        linewidth=0.8,
        edgecolor="#E2E8F0",
        facecolor="white",
        zorder=2,
    )
    fig.patches.append(patch)
    fig.text(x + 0.014, y + h - 0.028, title.upper(), fontsize=8, color=MUTED, weight="bold", zorder=3)
    fig.text(x + 0.014, y + 0.035, value, fontsize=20, color=DARK, weight="bold", zorder=3)
    if note:
        fig.text(x + w - 0.012, y + 0.039, note, fontsize=7.5, color=BLUE, ha="right", zorder=3)


def build_dashboard(kpis, monthly, customer_type, country, rfm, cohort):
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    fig.text(0.035, 0.953, "E-commerce User Growth Dashboard", fontsize=22, weight="bold", color=DARK)
    fig.text(
        0.035,
        0.922,
        "Customer growth, retention and value | UCI Online Retail | Dec 2010–Dec 2011",
        fontsize=9.5,
        color=MUTED,
    )
    fig.text(0.965, 0.947, "PORTFOLIO ANALYSIS", ha="right", fontsize=8, weight="bold", color=BLUE)

    values = dict(zip(kpis["Metric"], kpis["Value"]))
    cards = [
        ("Revenue", f"£{values['Revenue']/1_000_000:.2f}M", "valid purchases"),
        ("Orders", f"{values['Orders']:,.0f}", "completed"),
        ("Customers", f"{values['Customers']:,.0f}", "identified"),
        ("Average order value", f"£{values['AOV']:,.2f}", "per order"),
        ("Repeat customer rate", f"{values['Repeat Customer Rate']:.1%}", "2+ orders"),
    ]
    gap = 0.012
    card_w = (0.93 - gap * 4) / 5
    for i, card in enumerate(cards):
        add_card(fig, 0.035 + i * (card_w + gap), 0.805, card_w, 0.09, *card)

    gs = fig.add_gridspec(
        2, 3, left=0.045, right=0.965, bottom=0.12, top=0.76,
        width_ratios=[1.45, 1.15, 1.05], height_ratios=[1, 1], hspace=0.38, wspace=0.28
    )

    ax1 = fig.add_subplot(gs[0, :2]); style_axis(ax1)
    full = monthly[monthly["InvoiceMonth"].between("2011-01", "2011-11")]
    ax1.plot(full["InvoiceMonth"], full["Revenue"], color=BLUE, marker="o", linewidth=2.5, markersize=4)
    ax1.fill_between(range(len(full)), full["Revenue"], alpha=0.08, color=BLUE)
    ax1.set_title("Monthly revenue trend — complete months", loc="left", fontsize=11, weight="bold", color=DARK, pad=10)
    ax1.set_ylabel("Revenue", fontsize=8, color=MUTED)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"£{x/1_000_000:.1f}M"))
    ax1.tick_params(axis="x", rotation=35)
    peak = full.loc[full["Revenue"].idxmax()]
    ax1.annotate(
        f"Peak £{peak['Revenue']/1_000_000:.2f}M",
        (list(full["InvoiceMonth"]).index(peak["InvoiceMonth"]), peak["Revenue"]),
        xytext=(-50, 18), textcoords="offset points", fontsize=8, color=DARK_BLUE,
        arrowprops=dict(arrowstyle="->", color=DARK_BLUE, lw=0.8),
    )

    ax2 = fig.add_subplot(gs[0, 2]); style_axis(ax2)
    rfm_plot = rfm.sort_values("RevenueShare")
    ax2.barh(rfm_plot["Segment"], rfm_plot["RevenueShare"], color=[LIGHT_BLUE, LIGHT_BLUE, "#93C5FD", BLUE, DARK_BLUE])
    ax2.set_title("Revenue share by RFM segment", loc="left", fontsize=11, weight="bold", color=DARK, pad=10)
    ax2.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax2.set_xlabel("Revenue share", fontsize=8, color=MUTED)
    for i, value in enumerate(rfm_plot["RevenueShare"]):
        ax2.text(value + 0.008, i, f"{value:.1%}", va="center", fontsize=8, color=DARK)

    ax3 = fig.add_subplot(gs[1, 0]); style_axis(ax3)
    x = np.arange(len(customer_type))
    ax3.bar(x, customer_type.get("New", 0), color="#93C5FD", label="New")
    ax3.bar(x, customer_type.get("Returning", 0), bottom=customer_type.get("New", 0), color=BLUE, label="Returning")
    ax3.set_xticks(x, customer_type["InvoiceMonth"], rotation=45, ha="right")
    ax3.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"£{v/1_000_000:.1f}M"))
    ax3.set_title("New vs returning customer revenue", loc="left", fontsize=11, weight="bold", color=DARK, pad=10)
    ax3.legend(frameon=False, fontsize=8, ncol=2, loc="upper left")

    ax4 = fig.add_subplot(gs[1, 1]); style_axis(ax4)
    c = country.sort_values("Revenue")
    ax4.barh(c["Country"], c["Revenue"], color=AMBER)
    ax4.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"£{v/1_000:.0f}K"))
    ax4.set_title("Top international markets", loc="left", fontsize=11, weight="bold", color=DARK, pad=10)
    ax4.set_xlabel("Revenue", fontsize=8, color=MUTED)

    ax5 = fig.add_subplot(gs[1, 2])
    matrix = cohort.to_numpy(dtype=float)
    mask = np.isnan(matrix) | (matrix == 0)
    shown = np.ma.masked_where(mask, matrix)
    im = ax5.imshow(shown, cmap="Blues", vmin=0, vmax=0.55, aspect="auto")
    ax5.set_xticks(range(len(cohort.columns)), cohort.columns, fontsize=7)
    ax5.set_yticks(range(len(cohort.index)), cohort.index, fontsize=7)
    ax5.set_title("Monthly cohort retention", loc="left", fontsize=11, weight="bold", color=DARK, pad=10)
    ax5.set_xlabel("Months since acquisition", fontsize=8, color=MUTED)
    ax5.set_ylabel("Cohort", fontsize=8, color=MUTED)
    for spine in ax5.spines.values(): spine.set_visible(False)

    fig.text(
        0.045, 0.035,
        "Note: cancelled orders, non-positive values, anonymous customers and exact duplicates are excluded. Partial months are excluded from the primary trend.",
        fontsize=7.5, color=MUTED,
    )
    fig.savefig(OUTPUT / "ecommerce_growth_dashboard.png", dpi=180, facecolor=BG, bbox_inches="tight")
    fig.savefig(OUTPUT / "ecommerce_growth_dashboard.pdf", facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def main():
    df = load_data()
    sources = build_sources(df)
    build_dashboard(*sources)
    print(f"Dashboard saved to {OUTPUT / 'ecommerce_growth_dashboard.png'}")
    print(f"Tableau sources saved to {TABLEAU}")


if __name__ == "__main__":
    main()
