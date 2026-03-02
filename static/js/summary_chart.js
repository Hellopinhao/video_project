(() => {
  const chartEl = document.getElementById('timeChart');
  if (!chartEl || typeof Chart === 'undefined') return;

  const rawCategoryData = chartEl.dataset.categoryData || '[]';
  let categoryData = [];
  try {
    categoryData = JSON.parse(rawCategoryData);
  } catch {
    categoryData = [];
  }
  if (!Array.isArray(categoryData) || !categoryData.length) return;

  const labels = categoryData.map((cat) => cat.name);
  const data = categoryData.map((cat) => cat.percentage);

  const colors = [
    'rgba(66, 99, 235, 0.8)',
    'rgba(52, 211, 153, 0.8)',
    'rgba(251, 191, 36, 0.8)',
    'rgba(239, 68, 68, 0.8)',
    'rgba(168, 85, 247, 0.8)'
  ];

  new Chart(chartEl.getContext('2d'), {
    type: 'pie',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            font: {
              size: 14,
              family: "'Microsoft YaHei', sans-serif"
            },
            padding: 15
          }
        },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.label}: ${context.parsed.toFixed(2)}%`;
            }
          }
        }
      }
    }
  });
})();
