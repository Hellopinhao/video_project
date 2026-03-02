(() => {
  const canvas = document.getElementById('ageChart');
  if (!canvas || typeof Chart === 'undefined') return;

  const labels = ['10-29岁', '30-49岁', '50岁及以上'];
  const values = [28.6, 37.5, 33.9];

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
            padding: 15,
            font: {
              size: 14,
              family: "'Microsoft YaHei', sans-serif",
            },
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
