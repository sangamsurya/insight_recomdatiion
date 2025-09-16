# app.py
import os
import psycopg2
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# ================================
# Load environment variables
# ================================
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ================================
# Initialize Flask App
# ================================
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for the frontend to access the API

# ================================
# API Endpoints
# ================================
@app.route('/api/data', methods=['GET'])
def get_company_data():
    conn = None
    cur = None
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Fetch all companies and their financial data
        cur.execute("""
            SELECT id, symbol, cik, year, start_date, end_date, revenue, net_income, assets, liabilities
            FROM companies_raw;
        """)
        companies = cur.fetchall()

        # Fetch all recommendations
        cur.execute("""
            SELECT company_id, recommendation
            FROM company_recommendations;
        """)
        recommendations = cur.fetchall()

        # Format data into a dictionary
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

        recommendation_data = []
        for rec in recommendations:
            rec_dict = {
                "company_id": rec[0],
                "recommendation": rec[1]
            }
            recommendation_data.append(rec_dict)

        return jsonify({
            "companies": company_data,
            "recommendations": recommendation_data
        })

    except Exception as e:
        print(f"❌ Database error: {e}")
        return jsonify({"error": "Failed to fetch data"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# ================================
# Serve the Frontend
# ================================
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)