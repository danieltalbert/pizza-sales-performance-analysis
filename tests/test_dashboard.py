from pathlib import Path

import pandas as pd
import pytest

from src.create_dashboard import build_metrics, load_data, validate_data

FIXTURE = Path(__file__).parent / "fixtures" / "pizza_sales_sample.csv"


def test_fixture_produces_expected_headline_metrics():
    frame = load_data(FIXTURE)

    metrics = build_metrics(frame)

    assert metrics["revenue"] == pytest.approx(98.0)
    assert metrics["orders"] == 3
    assert metrics["pizzas"] == 7
    assert metrics["aov"] == pytest.approx(98 / 3)
    assert metrics["weekday_orders"].loc["Friday"] == 2


def test_validation_rejects_duplicate_line_identifiers():
    frame = pd.read_csv(FIXTURE)
    frame.loc[1, "order_details_id"] = frame.loc[0, "order_details_id"]

    with pytest.raises(ValueError, match="duplicate order_details_id"):
        validate_data(frame)


def test_validation_rejects_inconsistent_extended_price():
    frame = pd.read_csv(FIXTURE)
    frame.loc[0, "total_price"] = 999

    with pytest.raises(ValueError, match="quantity multiplied by unit_price"):
        validate_data(frame)
