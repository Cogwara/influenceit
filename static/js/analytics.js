function fetchMetrics(metricType, period = '30') {
    const url = `/analytics/metrics/${metricType}/?period=${period}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }

            // Update summary metrics
            updateSummaryMetrics(data.summary);

            // Update chart
            updateChart(metricType, data);
        })
        .catch(error => console.error('Error fetching metrics:', error));
}

function updateSummaryMetrics(summary) {
    // Update each metric in the summary section
    Object.entries(summary).forEach(([key, value]) => {
        const element = document.getElementById(`${key}-metric`);
        if (element) {
            if (key.includes('rate')) {
                element.textContent = `${value.toFixed(2)}%`;
            } else if (value > 1000) {
                element.textContent = value.toLocaleString();
            } else {
                element.textContent = value;
            }
        }
    });
}

function updateChart(metricType, data) {
    const chartId = `${metricType}Chart`;
    const ctx = document.getElementById(chartId)?.getContext('2d');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (window.charts && window.charts[chartId]) {
        window.charts[chartId].destroy();
    }

    // Initialize charts object if it doesn't exist
    if (!window.charts) window.charts = {};

    // Create new chart
    window.charts[chartId] = new Chart(ctx, {
        type: getChartType(metricType),
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: getChartOptions(metricType)
    });
}

function getChartType(metricType) {
    const chartTypes = {
        'engagement': 'bar',
        'revenue': 'line',
        'performance': 'bar'
    };
    return chartTypes[metricType] || 'bar';
}

function getChartOptions(metricType) {
    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            }
        }
    };

    const specificOptions = {
        'revenue': {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => '$' + value.toLocaleString()
                    }
                }
            }
        },
        'engagement': {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => value.toLocaleString()
                    }
                }
            }
        }
    };

    return {
        ...baseOptions,
        ...(specificOptions[metricType] || {})
    };
}

// Initialize metrics on page load
document.addEventListener('DOMContentLoaded', () => {
    const periodSelect = document.getElementById('period-select');
    if (periodSelect) {
        periodSelect.addEventListener('change', (e) => {
            const metricType = document.querySelector('[data-metric-type]')?.dataset.metricType;
            if (metricType) {
                fetchMetrics(metricType, e.target.value);
            }
        });
    }

    // Initial load of metrics
    const metricType = document.querySelector('[data-metric-type]')?.dataset.metricType;
    if (metricType) {
        fetchMetrics(metricType);
    }
}); 