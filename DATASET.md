# Dataset provenance

This project analyzes the **Pizza Place Sales** dataset distributed through the Maven Analytics Data Playground.

## Source and permission

- Publisher: [Maven Analytics](https://mavenanalytics.io/data-playground/pizza-place-sales)
- Original source credited by the publisher: Vincent Arel-Bundock (Rdatasets)
- Subject: one year of orders from a fictitious pizza restaurant
- Publisher license: **Public Domain**
- Dataset shape: 48,620 order-line records and 12 source fields
- Local representation: the four source tables are joined in `data/pizza_sales.xlsx`, sheet `pizza_sales`

The tracked workbook is included so the analysis is reproducible. The MIT License in this repository covers Daniel Talbert's original code and documentation; it does not replace or narrow the dataset's public-domain status.

## Fields

| Field | Meaning |
| --- | --- |
| `order_details_id` | Unique order-line identifier |
| `order_id` | Order identifier shared by its line items |
| `pizza_id` | Product and size identifier |
| `quantity` | Number of pizzas on the line |
| `order_date`, `order_time` | Order timestamp components |
| `unit_price`, `total_price` | Unit and extended sales values |
| `pizza_size`, `pizza_category` | Product grouping fields |
| `pizza_ingredients`, `pizza_name` | Menu description fields |

## Validation contract

`src/create_dashboard.py` refuses inputs with missing required fields, null required values, duplicate line identifiers, non-positive quantities/prices, or inconsistent extended prices. The repository test fixture is synthetic and exists only to exercise that contract.
