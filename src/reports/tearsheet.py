import os
import sqlite3
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

DB_PATH = "db/nifty100.db"

OUTPUT_DIR = "output/tearsheets"

PROS_CONS_FILE = "output/pros_cons_generated.csv"

CAPITAL_FILE = "output/capital_allocation.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------
# Styles
# -------------------------------------------------------

styles = getSampleStyleSheet()

title_style = styles["Heading1"]
title_style.alignment = TA_CENTER
title_style.textColor = colors.white

heading_style = styles["Heading2"]

normal_style = styles["BodyText"]

# -------------------------------------------------------
# Tearsheet Generator
# -------------------------------------------------------


class TearsheetGenerator:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.pros_cons = self.load_pros_cons()

        self.capital = self.load_capital_allocation()

    # ---------------------------------------------------

    def load_pros_cons(self):

        if os.path.exists(PROS_CONS_FILE):

            return pd.read_csv(PROS_CONS_FILE)

        return pd.DataFrame()

    # ---------------------------------------------------

    def load_capital_allocation(self):

        if os.path.exists(CAPITAL_FILE):

            return pd.read_csv(CAPITAL_FILE)

        return pd.DataFrame()

    # ---------------------------------------------------

    def create_kpi_tile(self, title, value):

        table = Table(
            [
                [Paragraph(f"<b>{title}</b>", heading_style)],
                [Paragraph(str(value), normal_style)]
            ],
            colWidths=[2.2 * inch]
        )

        table.setStyle(TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8EEF7")),

            ("BACKGROUND", (0, 1), (-1, -1), colors.white),

            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

            ("TOPPADDING", (0, 0), (-1, -1), 6)

        ]))

        return table
    
        # ---------------------------------------------------
    # Load company data
    # ---------------------------------------------------

    def load_company_data(self, company):

        company_df = pd.read_sql(
            f"""
            SELECT *
            FROM companies
            WHERE id='{company}'
            """,
            self.conn
        )

        ratios = pd.read_sql(
            f"""
            SELECT *
            FROM financial_ratios
            WHERE company_id='{company}'
            ORDER BY year
            """,
            self.conn
        )

        pnl = pd.read_sql(
            f"""
            SELECT *
            FROM profitandloss
            WHERE company_id='{company}'
            ORDER BY year
            """,
            self.conn
        )

        return company_df, ratios, pnl

    # ---------------------------------------------------
    # Revenue vs Profit Chart
    # ---------------------------------------------------

    def revenue_profit_chart(self, pnl):

        drawing = Drawing(420, 220)

        chart = VerticalBarChart()

        chart.x = 50
        chart.y = 40

        chart.width = 320
        chart.height = 140

        revenue = pnl["sales"].fillna(0).tolist()[-10:]
        profit = pnl["net_profit"].fillna(0).tolist()[-10:]

        years = pnl["year"].astype(str).tolist()[-10:]

        chart.data = [
            revenue,
            profit
        ]

        chart.categoryAxis.categoryNames = years

        chart.valueAxis.valueMin = 0

        chart.barSpacing = 2
        chart.groupSpacing = 8

        drawing.add(chart)

        return drawing

    # ---------------------------------------------------
    # ROE vs Debt-to-Equity
    # ---------------------------------------------------

    def roe_de_chart(self, ratios):

        drawing = Drawing(420, 220)

        chart = LinePlot()

        chart.x = 50
        chart.y = 35

        chart.width = 320
        chart.height = 140

        x = list(range(len(ratios.tail(10))))

        roe = ratios["return_on_equity_pct"].fillna(0).tolist()[-10:]

        debt = ratios["debt_to_equity"].fillna(0).tolist()[-10:]

        chart.data = [
            list(zip(x, roe)),
            list(zip(x, debt))
        ]

        chart.lines[0].symbol = makeMarker("Circle")
        chart.lines[1].symbol = makeMarker("Square")

        drawing.add(chart)

        return drawing

    # ---------------------------------------------------
    # Pros
    # ---------------------------------------------------

    def get_pros(self, company):

        if self.pros_cons.empty:
            return []

        df = self.pros_cons[
            (self.pros_cons["company_id"] == company)
            &
            (self.pros_cons["type"].str.lower() == "pro")
        ]

        return df["text"].head(5).tolist()

    # ---------------------------------------------------
    # Cons
    # ---------------------------------------------------

    def get_cons(self, company):

        if self.pros_cons.empty:
            return []

        df = self.pros_cons[
            (self.pros_cons["company_id"] == company)
            &
            (self.pros_cons["type"].str.lower() == "con")
        ]

        return df["text"].head(5).tolist()

    # ---------------------------------------------------
    # Capital Allocation
    # ---------------------------------------------------

    def get_capital_pattern(self, company):

        if self.capital.empty:
            return "N/A"

        df = self.capital[
            self.capital["company_id"] == company
        ]

        if df.empty:
            return "N/A"

        latest = df.sort_values("year").iloc[-1]

        return latest["pattern_label"]
    
        # ---------------------------------------------------
    # Create PDF
    # ---------------------------------------------------

    def create_pdf(self, company):

        company_df, ratios, pnl = self.load_company_data(company)

        if company_df.empty:
            print(f"{company} not found.")
            return

        if ratios.empty:
            print(f"No ratios found for {company}.")
            return

        if pnl.empty:
            print(f"No P&L found for {company}.")
            return

        latest_company = company_df.iloc[0]
        latest_ratio = ratios.iloc[-1]

        filename = os.path.join(
            OUTPUT_DIR,
            f"{company}.pdf"
        )

        doc = SimpleDocTemplate(
            filename,
            pagesize=(8.27 * inch, 11.69 * inch),
            leftMargin=20,
            rightMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        story = []

        # ---------------------------------------------------
        # Header
        # ---------------------------------------------------

        header = Table(
            [[
                Paragraph(
                    f"<b>{company}</b>",
                    title_style
                )
            ]],
            colWidths=[7.3 * inch]
        )

        header.setStyle(TableStyle([

            ("BACKGROUND",(0,0),(-1,-1),HexColor("#0B1F3A")),

            ("ALIGN",(0,0),(-1,-1),"CENTER"),

            ("TOPPADDING",(0,0),(-1,-1),10),

            ("BOTTOMPADDING",(0,0),(-1,-1),10)

        ]))

        story.append(header)

        story.append(Spacer(1,0.25*inch))

        # ---------------------------------------------------
        # KPI Tiles
        # ---------------------------------------------------

        kpis = [

            self.create_kpi_tile(
                "Book Value",
                round(latest_ratio.get("book_value_per_share",0),2)
            ),

            self.create_kpi_tile(
                "ROE",
                round(latest_ratio.get("return_on_equity_pct",0),2)
            ),

            self.create_kpi_tile(
                "Interest Coverage",
                round(latest_ratio.get("interest_coverage",0),2)
            ),

            self.create_kpi_tile(
                "Debt/Equity",
                round(latest_ratio.get("debt_to_equity",0),2)
            ),

            self.create_kpi_tile(
                "Revenue CAGR",
                round(latest_ratio.get("revenue_cagr_5yr",0),2)
            ),

            self.create_kpi_tile(
                "PAT CAGR",
                round(latest_ratio.get("pat_cagr_5yr",0),2)
            )

        ]

        kpi_table = Table(

            [

                kpis[:3],

                kpis[3:]

            ],

            colWidths=[2.3*inch]*3,

            rowHeights=[1.0*inch]*2

        )

        story.append(kpi_table)

        story.append(Spacer(1,0.25*inch))

        # ---------------------------------------------------
        # Revenue Chart
        # ---------------------------------------------------

        story.append(
            Paragraph(
                "<b>Revenue vs Net Profit (10 Years)</b>",
                heading_style
            )
        )

        story.append(
            self.revenue_profit_chart(pnl)
        )

        story.append(Spacer(1,0.25*inch))

        # ---------------------------------------------------
        # ROE Chart
        # ---------------------------------------------------

        story.append(
            Paragraph(
                "<b>ROE vs Debt-to-Equity</b>",
                heading_style
            )
        )

        story.append(
            self.roe_de_chart(ratios)
        )

        story.append(PageBreak())

                # ---------------------------------------------------
        # PAGE 2
        # ---------------------------------------------------

        story.append(
            Paragraph(
                "<b>Pros</b>",
                heading_style
            )
        )

        pros = self.get_pros(company)

        if pros:

            for item in pros:

                story.append(
                    Paragraph(f"• {item}", normal_style)
                )

        else:

            story.append(
                Paragraph("No Pros Available", normal_style)
            )

        story.append(Spacer(1,0.25*inch))

        # ---------------------------------------------------

        story.append(
            Paragraph(
                "<b>Cons</b>",
                heading_style
            )
        )

        cons = self.get_cons(company)

        if cons:

            for item in cons:

                story.append(
                    Paragraph(f"• {item}", normal_style)
                )

        else:

            story.append(
                Paragraph("No Cons Available", normal_style)
            )

        story.append(Spacer(1,0.30*inch))

        # ---------------------------------------------------

        pattern = self.get_capital_pattern(company)

        capital_table = Table(
            [[
                Paragraph(
                    f"<b>Capital Allocation :</b> {pattern}",
                    normal_style
                )
            ]],
            colWidths=[7.2*inch]
        )

        capital_table.setStyle(TableStyle([

            ("BACKGROUND",(0,0),(-1,-1),HexColor("#E8EEF7")),

            ("BOX",(0,0),(-1,-1),0.5,colors.grey),

            ("TOPPADDING",(0,0),(-1,-1),8),

            ("BOTTOMPADDING",(0,0),(-1,-1),8)

        ]))

        story.append(capital_table)

        story.append(Spacer(1,0.50*inch))

        story.append(
            Paragraph(
                "Generated using Nifty100 Financial Intelligence Platform",
                styles["Italic"]
            )
        )

        # ---------------------------------------------------

        doc.build(story)

        print(f"Created : {filename}")


# -------------------------------------------------------
# Main
# -------------------------------------------------------

if __name__ == "__main__":

    pdf = TearsheetGenerator()

    companies = [

        "TCS",

        "HDFCBANK",

        "RELIANCE",

        "SUNPHARMA",

        "TATASTEEL"

    ]

    for company in companies:

        try:

            pdf.create_pdf(company)

        except Exception as e:

            print(f"{company} -> {e}")