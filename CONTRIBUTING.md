# Contributing

Contributions should make the analysis easier to reproduce, audit, or use for a
real business decision.

## Before you start

1. Read [DATASET.md](DATASET.md) and the README's
   [analysis workflow](README.md#analysis-workflow).
2. Open an issue before changing KPI definitions, adding a data source, or
   redesigning the decision views.
3. Do not commit credentials, private business data, notebook caches,
   generated temporary outputs, or machine-specific absolute paths.

## Local checks

```bash
python -m pytest -q
python src/create_dashboard.py \
  --data tests/fixtures/pizza_sales_sample.csv \
  --output /tmp/pizza-figures
git diff --check
```

Changes to validation, aggregation, or KPI definitions should include a focused
test. If tracked figures change, regenerate them from the documented source and
explain the business interpretation in the pull request.

## Pull requests

Describe the question, the change, and the exact verification commands. Attach
publication-safe before/after visuals for chart changes and keep unrelated
cleanup in a separate pull request.
