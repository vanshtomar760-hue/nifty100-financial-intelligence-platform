# Sprint 2 Retrospective

## Overview

Sprint 2 focused on implementing and validating financial KPI calculations for the Nifty100 analytics platform.

## Work Completed

- Implemented profitability, leverage, efficiency, and cash flow KPIs.
- Added Free Cash Flow, CapEx Intensity, CFO Quality Score, and Capital Allocation metrics.
- Implemented Revenue, PAT, and EPS 5-Year CAGR calculations with edge-case handling.
- Populated the financial_ratios SQLite table with computed KPI values.
- Added Composite Quality Score using available CAGR values.
- Developed ROCE and ROE validation scripts against source data.
- Generated ratio_edge_cases.log for anomaly tracking.
- Added verification utilities for schema, row counts, and financial ratio validation.
- Verified all KPI unit tests successfully.

## Formula Decisions

- ROE = Net Profit / Equity × 100
- ROCE = EBIT / Capital Employed × 100
- Composite Quality Score = Average of available Revenue, PAT, and EPS CAGR values
- Debt-to-Equity warnings are suppressed for Financials sector companies.

## Edge Cases Handled

- Division by zero protection
- Missing financial values
- Negative CAGR scenarios
- Turnaround companies
- Zero-base companies
- Source value anomalies (e.g., TCS ROE)
- Financial sector leverage exceptions

## Validation Summary

- 93/93 unit tests passed.
- Financial ratios populated successfully.
- Manual spot-checks matched expected ROE and Revenue CAGR values.
- ROE and ROCE anomalies documented for further review.