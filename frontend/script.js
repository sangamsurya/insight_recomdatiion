document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

async function fetchData() {
    try {
        const response = await fetch('/api/data'); // Fetch data from your Flask API
        const data = await response.json();

        if (response.ok) {
            displayFinancialData(data.companies);
            displayRecommendations(data.companies, data.recommendations);
        } else {
            console.error('API Error:', data.error);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

function displayFinancialData(companies) {
    const tableBody = document.querySelector('#companies-table tbody');
    tableBody.innerHTML = ''; // Clear existing data

    companies.forEach(company => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${company.symbol}</td>
            <td>${company.revenue ? company.revenue.toLocaleString() : 'N/A'}</td>
            <td>${company.net_income ? company.net_income.toLocaleString() : 'N/A'}</td>
            <td>${company.assets ? company.assets.toLocaleString() : 'N/A'}</td>
            <td>${company.liabilities ? company.liabilities.toLocaleString() : 'N/A'}</td>
        `;
        tableBody.appendChild(row);
    });
}

function displayRecommendations(companies, recommendations) {
    const tableBody = document.querySelector('#recommendations-table tbody');
    tableBody.innerHTML = ''; // Clear existing data

    recommendations.forEach(rec => {
        const company = companies.find(c => c.id === rec.company_id);
        const symbol = company ? company.symbol : 'N/A';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${symbol}</td>
            <td>${rec.recommendation}</td>
        `;
        tableBody.appendChild(row);
    });
}