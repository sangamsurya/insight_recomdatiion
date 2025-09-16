import os
import psycopg2
import finnhub
from dotenv import load_dotenv


# Load environment variables from the .env file for secure configuration.
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


# Establish a connection to the PostgreSQL database using the URL from environment variables.
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create table for raw company financials
# Define the SQL command to create the companies_raw table if it doesn't exist.
# The table stores key financial metrics and uses 'symbol' as a unique key to prevent duplicates.
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

# Initialize the Finnhub API client with the API key.
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)


# import json

def fetch_company_financials(symbol: str):
    """
    Fetches the latest annual financial data for a given company symbol from Finnhub,
    parses key metrics, and stores them in the PostgreSQL database.

    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL').
    """
    try:
        # Request the latest annual financial report for the specified symbol.
        response = finnhub_client.financials_reported(symbol=symbol, freq='annual')
        
        # Check if the response contains valid data.
        if "data" not in response or not response["data"]:
            print(f"❌ No financial data found for {symbol}")
            return {}, None

        # Access the latest annual report from the 'data' list.
        report = response["data"][0]  
        rpt = report["report"]

        # Pretty print the full report for debugging and verification.
        # print(f"\n=== Full Annual Report for {symbol} ===")
        # print(json.dumps(rpt, indent=2))

        # Helper function to find a specific financial metric by its label in a list of items.
        def find_value(items, label):
            """Searches for a label-value pair and returns the value."""
            for item in items:
                if item["label"].lower() == label.lower():
                    return item["value"]
            return None

        # Extract 'balance sheet' (bs) and 'income statement' (ic) lists.
        bs = rpt.get("bs", [])
        ic = rpt.get("ic", [])

        # Extract specific financial metrics from the report using the helper function.
        revenue = find_value(ic, "Revenues")
        net_income = find_value(ic, "Net income")
        assets = find_value(bs, "Total assets")
        liabilities = find_value(bs, "Total liabilities")

        # Create a dictionary to hold the extracted financial data.
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
        # Use a single SQL query with 'ON CONFLICT' clause to either insert a new record
        # or update an existing one if the symbol already exists. This is an efficient "upsert".
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
        # Fetch the ID of the newly inserted/updated row.
        company_id = cur.fetchone()[0]
        # Commit the changes to the database.
        conn.commit()
        print(f"✅ Saved financials for {symbol}")
        # Return the financial data and the database ID.
        return financial_data, company_id

    except Exception as e:
        # Catch any exceptions during the process (e.g., API errors, network issues) and print an error message.
        print(f"❌ Error fetching data for {symbol}: {e}")
        return {}, None



if __name__ == "__main__":
    # A list of stock symbols to fetch data for.
    symbols = ["AAPL", "MSFT", "GOOGL"]
    # Loop through each symbol and call the data fetching function.
    for sym in symbols:
        fetch_company_financials(sym)