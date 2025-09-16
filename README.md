# 🚀 Financial Insights Engine

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3-lightgrey.svg)
![PostgreSQL](https://img.shields.io/badge/postgres-15-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![Deployment](https://img.shields.io/badge/deployed-Railway-purple.svg)

🔗 **Live Demo**: https://superb-learning-production.up.railway.app/

---

## 💡 Project Overview

The **Financial Insights Engine** is a full-stack application that automates the collection of public company financial data, uses AI to generate actionable insights, and visualizes results on a modern web dashboard.

It demonstrates a complete data-driven workflow — from **data ingestion → AI analysis → visualization**.

---

## ✨ Key Features

* 📊 **Automated Data Fetching** – Pulls annual financial reports from the **Finnhub API** (e.g., AAPL, MSFT, GOOGL).
* 🤖 **AI-Powered Analysis** – Uses the **Groq API** to generate concise business insights.
* 🗄 **Persistent Storage** – Stores raw financials + AI insights in **PostgreSQL**.
* 🔌 **RESTful API** – Flask backend exposes clean JSON endpoints.
* 📺 **Interactive Dashboard** – Simple, responsive UI displaying metrics + AI insights.
* 🐳 **Production Ready** – Dockerized and deployable on **Railway**.

---

## 🛠️ Technology Stack

* **Backend**: Python, Flask
* **Data Ingestion**: Python (Finnhub & Groq APIs)
* **Database**: PostgreSQL
* **Frontend**: HTML, CSS, JavaScript
* **Deployment**: Docker, Railway

---

## 📂 Project Structure

```
.
├── backend/
│   ├── app.py              # Flask API for data serving
│   ├── Dockerfile          # Backend Dockerfile
│   └── requirements.txt    # Backend dependencies
├── frontend/
│   ├── index.html          # Dashboard UI
│   ├── script.js           # Frontend logic
│   └── style.css           # Dashboard styles
├── scripts/
│   ├── Dockerfile          # Scripts Dockerfile
│   ├── hunter_fetch.py     # Fetches financial data
│   ├── groq_leads.py       # Generates AI insights
│   └── requirements.txt    # Script dependencies
├── .env                    # API keys & DB URL
└── .gitignore              # Ignore files
```

---

## 🗄 Database Schema

### `companies_raw`

| Column      | Type               | Notes             |
| ----------- | ------------------ | ----------------- |
| id          | SERIAL PRIMARY KEY |                   |
| symbol      | TEXT UNIQUE        | Company ticker    |
| cik         | TEXT               | SEC CIK code      |
| year        | INT                | Report year       |
| start\_date | DATE               | Report start      |
| end\_date   | DATE               | Report end        |
| revenue     | BIGINT             | Annual revenue    |
| net\_income | BIGINT             | Net income        |
| assets      | BIGINT             | Total assets      |
| liabilities | BIGINT             | Total liabilities |

### `company_recommendations`

| Column         | Type                              | Notes                |
| -------------- | --------------------------------- | -------------------- |
| id             | SERIAL PRIMARY KEY                |                      |
| company\_id    | INT REFERENCES companies\_raw(id) | Links to company     |
| recommendation | TEXT                              | AI-generated insight |

---

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sangamsurya/Financial-Insights-Engine
cd financial-insights-engine
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```ini
FINNHUB_API_KEY= your_finnhub_api_key
GROQ_API_KEY= your_groq_api_key
DATABASE_URL=postgres://user:password@host:port/database
```

### 3. Run Locally

#### Backend (Flask API)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Scripts (Data Fetching + AI Analysis)

```bash
cd ../scripts
pip install -r requirements.txt
python hunter_fetch.py
python groq_leads.py
```

Frontend will be served automatically by Flask at:
👉 [http://localhost:5000](http://localhost:5000)

---

## 🚀 Deployment on Railway

1. Push your code to **GitHub**.
2. Connect the repository to **Railway**.
3. Configure Railway to use:

   * `backend/Dockerfile` → Web service (Flask app + frontend).
   * `scripts/Dockerfile` → One-off job or scheduled task (data refresh).

