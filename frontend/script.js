document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        if (response.ok) {
            displayCompanyCards(data.companies, data.recommendations);
        } else {
            console.error('API Error:', data.error);
            showErrorState('Failed to load data. Please try again later.');
        }
    } catch (error) {
        console.error('Fetch error:', error);
        showErrorState('Network error. Unable to connect to the server.');
    }
}

function displayCompanyCards(companies, recommendations) {
    const container = document.getElementById('company-cards');
    container.innerHTML = '';

    if (companies.length === 0) {
        container.innerHTML = '<div class="no-data-message">No company data available.</div>';
        return;
    }

    companies.forEach(company => {
        const companyRec = recommendations.find(rec => rec.company_id === company.id);
        const card = document.createElement('div');
        card.className = 'company-card';

        let insightsHtml = '';
        let recommendationsHtml = '';
        let nextStepsHtml = '';

        if (companyRec) {
            const recText = companyRec.recommendation;

            // Parsing logic specific to each company's text format
            if (company.symbol === 'AAPL') {
                const parts = recText.split(/\* \*\*Recommendations\*\*:/);
                const insightsPart = parts[0];
                const recommendationsPart = parts[1] || '';

                // Extract insights and metrics from the first part
                const insights = insightsPart.match(/\*\*Revenue\*\*:(.*?)\* \*\*Net Income\*\*:(.*?)\* \*\*Asset and Liability Management\*\*:(.*)/s);
                if (insights) {
                    insightsHtml += `<li><strong>Revenue:</strong>${insights[1].trim()}</li>`;
                    insightsHtml += `<li><strong>Net Income:</strong>${insights[2].trim()}</li>`;
                    insightsHtml += `<li><strong>Asset and Liability Management:</strong>${insights[3].trim()}</li>`;
                }
                
                // Extract recommendations from the second part
                if (recommendationsPart) {
                    recommendationsHtml = splitAndFormat(recommendationsPart.trim(), /\s\+\s/g).join('');
                }

            } else if (company.symbol === 'MSFT') {
                const parts = recText.split(/\*\*Recommendations:\*\*|\*\*Next Steps:\*\*/);
                const insights = parts[0].match(/\*\*Key Insights:\*\*(.*)/s);
                if (insights) insightsHtml = splitAndFormat(insights[1].trim(), '-').join('');

                if (parts[1]) recommendationsHtml = splitAndFormat(parts[1].trim(), /\d+\.\s/).join('');
                
                if (parts[2]) nextStepsHtml = splitAndFormat(parts[2].trim(), '-').join('');

            } else if (company.symbol === 'GOOGL') {
                const parts = recText.split(/\*\*Recommendations\*\*/);
                const insightsSection = parts[0];
                const recommendationsSection = parts[1];
                
                const insightPoints = insightsSection.split(/\*\*(.*?)\*\*/).filter(Boolean);
                let currentInsight = '';
                insightPoints.forEach((point, index) => {
                    if (index % 2 !== 0) {
                        currentInsight = `<li><strong>${point.trim()}</strong>`;
                    } else if (currentInsight) {
                        currentInsight += `${point.trim().replace(/:|-/g, '')}</li>`;
                        insightsHtml += currentInsight;
                        currentInsight = '';
                    }
                });

                if (recommendationsSection) {
                    const recPoints = recommendationsSection.split(/\d+\.\s/);
                    recPoints.forEach((point) => {
                        const trimmedPoint = point.trim();
                        if (trimmedPoint) {
                            recommendationsHtml += `<li>${trimmedPoint.replace(/\*\*|:/g, '')}</li>`;
                        }
                    });
                }
            }
        }
        
        if (!insightsHtml) insightsHtml = '<li>No insights available.</li>';
        if (!recommendationsHtml) recommendationsHtml = '<li>No recommendations available.</li>';
        if (!nextStepsHtml) nextStepsHtml = '<li>No next steps available.</li>';

        card.innerHTML = `
            <div class="card-header">
                <span class="symbol">${company.symbol}</span>
                <h2>${company.name || ''}</h2>
            </div>
            <div class="financial-data">
                <div class="metric">
                    <p class="metric-label">Revenue</p>
                    <span class="metric-value">${company.revenue ? formatCurrency(company.revenue) : 'N/A'}</span>
                </div>
                <div class="metric">
                    <p class="metric-label">Net Income</p>
                    <span class="metric-value">${company.net_income ? formatCurrency(company.net_income) : 'N/A'}</span>
                </div>
                <div class="metric">
                    <p class="metric-label">Assets</p>
                    <span class="metric-value">${company.assets ? formatCurrency(company.assets) : 'N/A'}</span>
                </div>
                <div class="metric">
                    <p class="metric-label">Liabilities</p>
                    <span class="metric-value">${company.liabilities ? formatCurrency(company.liabilities) : 'N/A'}</span>
                </div>
            </div>
            <div class="recommendations-section" onclick="toggleRecommendations(this)">
                <h3>
                    Recommendations
                    <i class="fas fa-chevron-right accordion-icon"></i>
                </h3>
                <ul class="recommendations-list">
                    <div class="recommendation-group">
                        <p><strong>Key Insights:</strong></p>
                        <ul>${insightsHtml}</ul>
                    </div>
                    <div class="recommendation-group">
                        <p><strong>Recommendations:</strong></p>
                        <ol>${recommendationsHtml}</ol>
                    </div>
                    <div class="recommendation-group">
                        <p><strong>Next Steps:</strong></p>
                        <ul>${nextStepsHtml}</ul>
                    </div>
                </ul>
            </div>
        `;
        container.appendChild(card);
    });
}

function splitAndFormat(text, delimiter) {
    if (!text) return [];
    let items = text.split(delimiter).filter(item => item.trim() !== '');
    return items.map(item => {
        let cleanItem = item.trim().replace(/\*+/g, '').replace(/^-/, '').trim();
        return `<li>${cleanItem}</li>`;
    });
}

function toggleRecommendations(element) {
    const list = element.querySelector('.recommendations-list');
    const icon = element.querySelector('.accordion-icon');
    list.classList.toggle('show');
    icon.classList.toggle('rotate');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function showErrorState(message) {
    const container = document.getElementById('company-cards');
    container.innerHTML = `<div class="error-message">${message}</div>`;
}