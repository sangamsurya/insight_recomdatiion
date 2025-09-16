import os
import psycopg2
import requests
from dotenv import load_dotenv

# ================================
# Load environment variables
# ================================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# ================================
# Connect to PostgreSQL
# ================================
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create table for recommendations
cur.execute("""
CREATE TABLE IF NOT EXISTS company_recommendations (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies_raw(id),
    recommendation TEXT
);
""")
conn.commit()

# ================================
# Generate insights via Groq
# ================================
def generate_insights(financial_data: dict) -> str:
    summary = f"Company financials: {financial_data}" if financial_data else "No financial data available."

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a business analyst providing company performance insights."},
            {"role": "user", "content": f"Generate performance insights and recommendations based on this data:\n{summary}"}
        ],
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Groq API error: {e}"

# ================================
# Save recommendation
# ================================
def save_recommendation(company_id: int, recommendation: str):
    cur.execute("""
        INSERT INTO company_recommendations (company_id, recommendation)
        VALUES (%s, %s)
    """, (company_id, recommendation))
    conn.commit()
    print(f"✅ Recommendation saved for company ID {company_id}")

# ================================
# Main workflow
# ================================
if __name__ == "__main__":
    # Fetch companies from DB
    cur.execute("SELECT id, symbol, cik, year, start_date, end_date, revenue, net_income, assets, liabilities FROM companies_raw;")
    companies = cur.fetchall()

    for comp in companies:
        company_dict = {
            "symbol": comp[1],
            "cik": comp[2],
            "year": comp[3],
            "start_date": str(comp[4]),
            "end_date": str(comp[5]),
            "revenue": comp[6],
            "net_income": comp[7],
            "assets": comp[8],
            "liabilities": comp[9]
        }
        recommendation = generate_insights(company_dict)
        save_recommendation(comp[0], recommendation)
