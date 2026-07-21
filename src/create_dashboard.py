"""Validate the pizza-sales dataset and generate presentation figures.

Run from anywhere with:
    python src/create_dashboard.py
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "pizza_sales.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures"

REQUIRED_COLUMNS = {
    "order_details_id",
    "order_id",
    "pizza_id",
    "quantity",
    "order_date",
    "order_time",
    "unit_price",
    "total_price",
    "pizza_size",
    "pizza_category",
    "pizza_ingredients",
    "pizza_name",
}

COLORS = {
    "ink": "#17324D",
    "muted": "#657786",
    "accent": "#D95D39",
    "gold": "#E9A23B",
    "cream": "#F7F3EC",
    "grid": "#DCE3E8",
    "white": "#FFFFFF",
}


def validate_data(frame: pd.DataFrame) -> None:
    """Raise a useful error when the input cannot support the analysis."""
    missing_columns = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")
    if frame.empty:
        raise ValueError("Dataset contains no sales rows")
    if frame[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Dataset contains missing values in required columns")
    if frame["order_details_id"].duplicated().any():
        raise ValueError("Dataset contains duplicate order_details_id values")
    if (frame["quantity"] <= 0).any() or (frame["unit_price"] <= 0).any():
        raise ValueError("Quantity and unit price must be positive")
    expected_total = frame["quantity"] * frame["unit_price"]
    if not expected_total.round(2).equals(frame["total_price"].round(2)):
        raise ValueError("total_price does not match quantity multiplied by unit_price")


def load_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    """Load a CSV or workbook, validate it, and add analysis fields."""
    if data_path.suffix.lower() == ".csv":
        frame = pd.read_csv(data_path)
    else:
        frame = pd.read_excel(data_path, sheet_name="pizza_sales")
    validate_data(frame)
    frame["order_datetime"] = pd.to_datetime(
        frame["order_date"].astype(str) + " " + frame["order_time"].astype(str)
    )
    frame["day_of_week"] = frame["order_datetime"].dt.day_name()
    frame["hour"] = frame["order_datetime"].dt.hour
    return frame


def build_metrics(frame: pd.DataFrame) -> dict[str, object]:
    """Create the aggregates used by the dashboard and exported charts."""
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    order_totals = frame.groupby("order_id")["total_price"].sum()
    return {
        "revenue": frame["total_price"].sum(),
        "orders": frame["order_id"].nunique(),
        "pizzas": frame["quantity"].sum(),
        "aov": order_totals.mean(),
        "top_pizzas": (frame.groupby("pizza_name")["total_price"].sum().nlargest(5).sort_values()),
        "weekday_orders": (frame.groupby("day_of_week")["order_id"].nunique().reindex(day_order)),
        "hourly_orders": frame.groupby("hour")["order_id"].nunique(),
    }


def clean_pizza_name(name: str) -> str:
    """Shorten product labels while keeping them recognizable."""
    return name.removeprefix("The ").removesuffix(" Pizza")


def style_axis(axis: plt.Axes, grid_axis: str = "y") -> None:
    """Apply a consistent, presentation-ready chart style."""
    axis.set_facecolor(COLORS["white"])
    axis.tick_params(colors=COLORS["muted"], labelsize=9, length=0)
    axis.grid(axis=grid_axis, color=COLORS["grid"], linewidth=0.8, alpha=0.8)
    axis.set_axisbelow(True)
    for spine in axis.spines.values():
        spine.set_visible(False)


def save_supporting_figures(metrics: dict[str, object], output_dir: Path = OUTPUT_DIR) -> None:
    """Export focused versions of each chart for reuse outside the dashboard."""
    output_dir.mkdir(parents=True, exist_ok=True)

    top_pizzas = metrics["top_pizzas"]
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLORS["white"])
    labels = [clean_pizza_name(name) for name in top_pizzas.index]
    bars = ax.barh(labels, top_pizzas.values, color=COLORS["accent"])
    style_axis(ax, "x")
    ax.set_title("Top 5 pizzas by revenue", loc="left", color=COLORS["ink"], weight="bold")
    ax.set_xlabel("Revenue", color=COLORS["muted"])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1000:.0f}K"))
    ax.bar_label(bars, labels=[f"${value / 1000:.1f}K" for value in top_pizzas.values], padding=5)
    fig.tight_layout()
    fig.savefig(output_dir / "top_5_pizzas_by_revenue.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    weekday_orders = metrics["weekday_orders"]
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=COLORS["white"])
    colors = [
        COLORS["accent"] if day == "Friday" else COLORS["ink"] for day in weekday_orders.index
    ]
    bars = ax.bar(weekday_orders.index, weekday_orders.values, color=colors)
    style_axis(ax)
    ax.set_title("Orders by weekday", loc="left", color=COLORS["ink"], weight="bold")
    ax.set_ylabel("Unique orders", color=COLORS["muted"])
    ax.bar_label(bars, padding=4, fontsize=9)
    fig.tight_layout()
    fig.savefig(output_dir / "orders_by_weekday.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    hourly_orders = metrics["hourly_orders"]
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=COLORS["white"])
    ax.plot(
        hourly_orders.index, hourly_orders.values, color=COLORS["accent"], linewidth=2.5, marker="o"
    )
    style_axis(ax)
    ax.set_title("Orders by hour", loc="left", color=COLORS["ink"], weight="bold")
    ax.set_xlabel("Hour of day", color=COLORS["muted"])
    ax.set_ylabel("Unique orders", color=COLORS["muted"])
    ax.set_xticks(hourly_orders.index)
    fig.tight_layout()
    fig.savefig(output_dir / "orders_by_hour.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_dashboard(
    frame: pd.DataFrame,
    metrics: dict[str, object],
    output_dir: Path = OUTPUT_DIR,
) -> None:
    """Export a one-page dashboard optimized for the repository README."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 10), facecolor=COLORS["cream"])
    grid = fig.add_gridspec(
        3,
        6,
        height_ratios=[0.9, 2.5, 2.5],
        hspace=0.55,
        wspace=1.5,
        left=0.105,
        right=0.96,
        top=0.84,
        bottom=0.08,
    )

    fig.text(0.06, 0.94, "PIZZA SALES PERFORMANCE", fontsize=24, weight="bold", color=COLORS["ink"])
    fig.text(
        0.06,
        0.90,
        "One year of order data · January–December 2015",
        fontsize=12,
        color=COLORS["muted"],
    )

    kpis = [
        ("TOTAL REVENUE", f"${metrics['revenue']:,.0f}"),
        ("UNIQUE ORDERS", f"{metrics['orders']:,}"),
        ("PIZZAS SOLD", f"{metrics['pizzas']:,}"),
        ("AVG. ORDER VALUE", f"${metrics['aov']:,.2f}"),
    ]
    for index, (label, value) in enumerate(kpis):
        x_position = 0.06 + index * 0.225
        card = fig.add_axes([x_position, 0.755, 0.195, 0.095])
        card.set_facecolor(COLORS["white"])
        card.set_xticks([])
        card.set_yticks([])
        for spine in card.spines.values():
            spine.set_color(COLORS["grid"])
            spine.set_linewidth(1)
        card.text(0.06, 0.68, label, fontsize=9, color=COLORS["muted"], transform=card.transAxes)
        card.text(
            0.06,
            0.18,
            value,
            fontsize=18,
            weight="bold",
            color=COLORS["ink"],
            transform=card.transAxes,
        )

    top_axis = fig.add_subplot(grid[1:, :3])
    top_pizzas = metrics["top_pizzas"]
    top_labels = [clean_pizza_name(name) for name in top_pizzas.index]
    bars = top_axis.barh(top_labels, top_pizzas.values, color=COLORS["accent"], height=0.62)
    style_axis(top_axis, "x")
    top_axis.set_title(
        "Top products by revenue", loc="left", color=COLORS["ink"], weight="bold", pad=14
    )
    top_axis.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1000:.0f}K"))
    top_axis.bar_label(
        bars,
        labels=[f"${value / 1000:.1f}K" for value in top_pizzas.values],
        padding=5,
        fontsize=9,
        color=COLORS["ink"],
    )
    top_axis.margins(x=0.16)

    weekday_axis = fig.add_subplot(grid[1, 3:])
    weekday_orders = metrics["weekday_orders"]
    weekday_colors = [
        COLORS["accent"] if day == "Friday" else COLORS["ink"] for day in weekday_orders.index
    ]
    weekday_bars = weekday_axis.bar(
        [day[:3] for day in weekday_orders.index],
        weekday_orders.values,
        color=weekday_colors,
        width=0.64,
    )
    style_axis(weekday_axis)
    weekday_axis.set_title(
        "Demand builds toward Friday", loc="left", color=COLORS["ink"], weight="bold", pad=12
    )
    weekday_axis.set_ylabel("Orders", color=COLORS["muted"], fontsize=9)
    weekday_axis.set_ylim(0, 3900)
    weekday_axis.bar_label(weekday_bars, padding=3, fontsize=8, color=COLORS["ink"])

    hourly_axis = fig.add_subplot(grid[2, 3:])
    hourly_orders = metrics["hourly_orders"]
    hourly_axis.plot(
        hourly_orders.index,
        hourly_orders.values,
        color=COLORS["accent"],
        linewidth=2.5,
        marker="o",
        markersize=4,
    )
    style_axis(hourly_axis)
    hourly_axis.set_title(
        "Lunch and dinner drive order volume",
        loc="left",
        color=COLORS["ink"],
        weight="bold",
        pad=12,
    )
    hourly_axis.set_xlabel("Hour of day", color=COLORS["muted"], fontsize=9)
    hourly_axis.set_ylabel("Orders", color=COLORS["muted"], fontsize=9)
    hourly_axis.set_xticks(range(9, 24, 2))
    hourly_axis.annotate(
        "Peak: noon",
        xy=(12, hourly_orders.loc[12]),
        xytext=(13.4, hourly_orders.loc[12] + 140),
        color=COLORS["ink"],
        fontsize=9,
        arrowprops={"arrowstyle": "-", "color": COLORS["muted"]},
    )

    date_min = frame["order_datetime"].min().strftime("%b %Y")
    date_max = frame["order_datetime"].max().strftime("%b %Y")
    fig.text(
        0.06,
        0.025,
        f"Source: Pizza Sales workbook  ·  {len(frame):,} line items  ·  {date_min}–{date_max}",
        fontsize=9,
        color=COLORS["muted"],
    )
    fig.savefig(output_dir / "pizza_sales_dashboard.png", dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH, help="Input .xlsx or .csv file")
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for generated PNG files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = load_data(args.data)
    metrics = build_metrics(frame)
    save_supporting_figures(metrics, args.output)
    save_dashboard(frame, metrics, args.output)
    print(f"Dashboard and figures written to {args.output}")


if __name__ == "__main__":
    main()
