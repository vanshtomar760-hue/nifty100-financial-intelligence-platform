# Sprint 4 Retrospective

## UX Decisions

- Designed a clean and consistent dashboard layout for financial analysis.
- Used KPI cards and summary tables for quick interpretation of company performance.
- Organized reports and analytics into separate modules for easier navigation.
- Standardized report formats and naming conventions across all generated outputs.
- Improved readability of generated PDFs with proper spacing, headings, and table formatting.

## Data Edge Cases Discovered

- Several companies had incomplete financial records across years.
- Missing values in financial ratios required null handling to prevent runtime errors.
- Some companies had fewer than three years of historical data and were skipped during batch report generation.
- Differences between company IDs and company names required careful joins across tables.
- Certain metrics were unavailable for specific companies and were displayed as "N/A" instead of causing failures.

## Performance Findings

- Optimized SQLite queries by loading required datasets once and processing them with Pandas.
- Reduced repeated database queries during report generation.
- Batch tearsheet generation successfully processed 89 companies while automatically skipping unsupported cases.
- Sector reports were generated efficiently using grouped datasets.
- Overall reporting pipeline completed within a reasonable execution time for the complete NIFTY 100 dataset.

## Lessons Learned

- Robust validation is essential before performing financial calculations.
- Modular analytics functions simplify maintenance and future enhancements.
- Automated report generation significantly improves scalability over manual analysis.
- Proper exception handling prevents batch processes from failing due to isolated data issues.