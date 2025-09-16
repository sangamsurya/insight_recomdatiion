import os
import psycopg2
import finnhub
from dotenv import load_dotenv

# ================================
# Load environment variables
# ================================
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# ================================
# Connect to PostgreSQL
# ================================
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create table for raw company financials
cur.execute("""
CREATE TABLE IF NOT EXISTS companies_raw (
    id SERIAL PRIMARY KEY,
    symbol TEXT UNIQUE,
    cik TEXT,
    year INT,
    start_date DATE,
    end_date DATE,
    revenue BIGINT,
    net_income BIGINT,
    assets BIGINT,
    liabilities BIGINT
);
""")
conn.commit()

# ================================
# Initialize Finnhub client
# ================================
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# ================================
# Fetch company financials
# ================================
import json

def fetch_company_financials(symbol: str):
    try:
        response = finnhub_client.financials_reported(symbol=symbol, freq='annual')
        
        if "data" not in response or not response["data"]:
            print(f"❌ No financial data for {symbol}")
            return {}, None

        report = response["data"][0]  # latest annual report
        rpt = report["report"]

        # Pretty print the full report
        print(f"\n=== Full Annual Report for {symbol} ===")
        print(json.dumps(rpt, indent=2))

        # Helper function to find a value by label
        def find_value(items, label):
            for item in items:
                if item["label"].lower() == label.lower():
                    return item["value"]
            return None

        # Convert bs and ic lists
        bs = rpt.get("bs", [])
        ic = rpt.get("ic", [])

        # Extract key values
        revenue = find_value(ic, "Revenues")
        net_income = find_value(ic, "Net income")
        assets = find_value(bs, "Total assets")
        liabilities = find_value(bs, "Total liabilities")

        financial_data = {
            "symbol": response.get("symbol"),
            "cik": response.get("cik"),
            "year": report.get("year"),
            "start_date": report.get("startDate"),
            "end_date": report.get("endDate"),
            "revenue": revenue,
            "net_income": net_income,
            "assets": assets,
            "liabilities": liabilities
        }


        # Save to DB
        cur.execute("""
            INSERT INTO companies_raw (symbol, cik, year, start_date, end_date, revenue, net_income, assets, liabilities)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE
            SET cik = EXCLUDED.cik,
                year = EXCLUDED.year,
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                revenue = EXCLUDED.revenue,
                net_income = EXCLUDED.net_income,
                assets = EXCLUDED.assets,
                liabilities = EXCLUDED.liabilities
            RETURNING id;
        """, (
            financial_data["symbol"],
            financial_data["cik"],
            financial_data["year"],
            financial_data["start_date"],
            financial_data["end_date"],
            financial_data["revenue"],
            financial_data["net_income"],
            financial_data["assets"],
            financial_data["liabilities"]
        ))
        company_id = cur.fetchone()[0]
        conn.commit()
        print(f"✅ Saved financials for {symbol}")
        return financial_data, company_id

    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {e}")
        return {}, None

# ================================
# Example usage
# ================================
if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "GOOGL"]
    for sym in symbols:
        fetch_company_financials(sym)
