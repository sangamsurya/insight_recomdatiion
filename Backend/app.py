# app.py
import os
import psycopg2
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv


# Load environment variables from the .env file.
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


# Initialize the Flask application.
# The static_folder is set to '../frontend' to serve static files from the frontend directory.
# The static_url_path is set to '' so that files like index.html are served from the root URL.
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for all routes.
           # This is crucial to allow the frontend (running on a different port/origin)
           # to make API requests to this backend.


@app.route('/api/data', methods=['GET'])
def get_company_data():
    """
    API endpoint to fetch all company financial data and their AI-generated recommendations.
    Connects to the PostgreSQL database, queries two tables, and returns a combined JSON response.
    """
    conn = None
    cur = None
    try:
        # Connect to PostgreSQL using the connection string from environment variables.
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Fetch all records from the 'companies_raw' table.
        cur.execute("""
            SELECT id, symbol, cik, year, start_date, end_date, revenue, net_income, assets, liabilities
            FROM companies_raw;
        """)
        companies = cur.fetchall()

        # Fetch all records from the 'company_recommendations' table.
        cur.execute("""
            SELECT company_id, recommendation
            FROM company_recommendations;
        """)
        recommendations = cur.fetchall()

        # Format the raw database data into a list of dictionaries for the companies.
        company_data = []
        for comp in companies:
            company_dict = {
                "id": comp[0],
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
            company_data.append(company_dict)

        # Format the raw database data into a list of dictionaries for the recommendations.
        recommendation_data = []
        for rec in recommendations:
            rec_dict = {
                "company_id": rec[0],
                "recommendation": rec[1]
            }
            recommendation_data.append(rec_dict)

        # Return a single JSON response containing both datasets.
        return jsonify({
            "companies": company_data,
            "recommendations": recommendation_data
        })

    except Exception as e:
        # If any error occurs (e.g., database connection failure),
        # print the error and return a 500 Internal Server Error response.
        print(f"❌ Database error: {e}")
        return jsonify({"error": "Failed to fetch data"}), 500
    finally:
        # This block ensures that the database connection is always closed,
        # regardless of whether an error occurred.
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route('/')
def serve_index():
    """
    Serves the main index.html file from the frontend directory.
    This is the entry point for the web application.
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """
    Serves other static files (CSS, JS, images, etc.) from the frontend directory.
    The <path:path> variable captures the rest of the URL path.
    """
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    # Get the port from the environment variable 'PORT' or default to 8000.
    port = int(os.environ.get("PORT", 8000))
    # Run the Flask app on all available network interfaces ('0.0.0.0').
    # This allows it to be accessible externally, e.g., in a Docker container.
    app.run(host='0.0.0.0', port=port)