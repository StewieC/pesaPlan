document.addEventListener('DOMContentLoaded', function() {
  const ctx = document.getElementById('budgetChart').getContext('2d');
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: window.chartData.labels,
      datasets: [{
        data: window.chartData.data,
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' }
      }
    }
  });
});