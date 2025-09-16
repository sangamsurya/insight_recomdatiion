import os
import psycopg2
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to the PostgreSQL database using the connection string from environment variables
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create a table to store AI-generated company recommendations if it doesn't already exist.
# The table links to the companies_raw table via a foreign key.
cur.execute("""
CREATE TABLE IF NOT EXISTS company_recommendations (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies_raw(id),
    recommendation TEXT
);
""")
# Commit the changes to the database to finalize the table creation.
conn.commit()


# Function to generate financial insights using the Groq API.
def generate_insights(financial_data: dict) -> str:
    """
    Sends financial data to the Groq API to receive a performance analysis.

    Args:
        financial_data (dict): A dictionary containing a company's financial metrics.

    Returns:
        str: A string with the AI-generated insights or an error message if the API call fails.
    """
    # Create a summary of the financial data to be used in the API prompt.
    summary = f"Company financials: {financial_data}" if financial_data else "No financial data available."

    # Define the payload for the Groq API request.
    # It specifies the model, system and user messages, and a temperature for response creativity.
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a business analyst providing company performance insights in 200 words."},
            {"role": "user", "content": f"Generate performance insights and recommendations based on this data in only 200 words:\n{summary}"}
        ],
        "temperature": 0.7  # A lower temperature makes the response more predictable and focused.
    }

    # Set the request headers, including the authorization token for the Groq API.
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Make a POST request to the Groq API endpoint.
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        # Raise an HTTPError if the response status code is 4xx or 5xx.
        response.raise_for_status()
        # Parse the JSON response from the API.
        result = response.json()
        # Extract and return the generated content from the response.
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        # If an error occurs during the request, return an error message.
        return f"❌ Groq API error: {e}"

# Function to save a generated recommendation to the database.
def save_recommendation(company_id: int, recommendation: str):
    """
    Inserts a new recommendation into the company_recommendations table.

    Args:
        company_id (int): The unique ID of the company.
        recommendation (str): The text of the recommendation.
    """
    # Use a parameterized query to prevent SQL injection attacks.
    cur.execute("""
        INSERT INTO company_recommendations (company_id, recommendation)
        VALUES (%s, %s)
    """, (company_id, recommendation))
    # Commit the transaction to save the new record permanently.
    conn.commit()
    print(f"✅ Recommendation saved for company ID {company_id}")


# Main execution block. This code runs when the script is executed.
if __name__ == "__main__":
    # Fetch all records from the companies_raw table.
    cur.execute("SELECT id, symbol, cik, year, start_date, end_date, revenue, net_income, assets, liabilities FROM companies_raw;")
    companies = cur.fetchall()

    # Iterate through each company record fetched from the database.
    for comp in companies:
        # Create a dictionary from the fetched tuple to pass to the insights function.
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
        # Generate the recommendation using the company's financial data.
        recommendation = generate_insights(company_dict)
        # Save the generated recommendation to the database.
        save_recommendation(comp[0], recommendation)

    # Close the cursor and connection to the database to free up resources.
    cur.close()
    conn.close()