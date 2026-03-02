(() => {
  const canvas = document.getElementById('usageChart');
  if (!canvas || typeof Chart === 'undefined') return;

  const labels = ['生活类', '娱乐搞笑类', '新闻类'];
  const values = [36.54, 32.77, 31.73];
  const colors = [
    'rgba(66, 99, 235, 0.8)',
    'rgba(52, 211, 153, 0.8)',
    'rgba(251, 191, 36, 0.8)',
  ];

  new Chart(canvas.getContext('2d'), {
    type: 'pie',
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: colors,
          borderColor: '#fff',
          borderWidth: 2,
        },
      ],
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
              family: "'Microsoft YaHei', sans-serif",
            },
            padding: 15,
          },
        },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.label}: ${Number(context.parsed).toFixed(2)}%`;
            },
          },
        },
      },
    },
  });
})();
