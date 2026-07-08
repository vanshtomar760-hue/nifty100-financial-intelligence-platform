import os
import pandas as pd


def export_screeners(results):
    """
    Export all screener presets to one Excel workbook.
    """

    os.makedirs("output", exist_ok=True)

    output_file = "output/screener_output.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:

        for sheet_name, df in results.items():

            df.to_excel(
                writer,
                sheet_name=sheet_name[:31],   # Excel sheet limit
                index=False
            )

    print("\nExcel exported successfully!")
    print(output_file)