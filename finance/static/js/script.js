// /static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
  const chartCanvas = document.getElementById('budgetChart');
  
  // Only run the chart script if the canvas element exists
  if (chartCanvas && typeof window.chartData !== 'undefined') {
    const ctx = chartCanvas.getContext('2d');
    
    // New color palette for the chart
    const chartColors = [
        '#3DDC97', // Accent Green
        '#415A77', // Muted Blue
        '#778DA9', // Lighter Blue
        '#FFC107', // Warning Yellow
        '#0D1B2A', // Very Dark Blue
        '#E53935'  // Error Red
    ];

    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: window.chartData.labels,
        datasets: [{
          data: window.chartData.data,
          backgroundColor: chartColors,
          borderColor: '#ffffff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#0D1B2A', // Dark text for legend
              font: {
                size: 14
              }
            }
          }
        }
      }
    });
  }
});