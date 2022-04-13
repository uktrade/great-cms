import Plotly from 'plotly.js-dist-min'

const initTradeChart = () => {
  const config = {
    displayModeBar: false,
    responsive: true,
    locale: 'en-GB',
  }

  const layout = {
    yaxis: {
      fixedrange: true,
      rangemode: 'tozero',
    },
    xaxis: {
      fixedrange: true,
      showgrid: false,
      showticklabels: true,
      tickmode: 'linear',
      showspikes: true,
      spikethickness: 2,
      spikemode: 'across',
    },
    font: {
      family: 'Roboto, sans-serif',
      size: 18,
    },
    legend: {
      orientation: 'h',
    },
    colorway: ['#006ccc', '#ef5f56', '#00A699', '#666666'],
    margin: {
      b: 0,
      t: 0,
      l: 50,
      r: 0,
      pad: 10,
    },
  }

  const lines = [
    {
      title: 'Total trade',
      key: 'total',
    },
    {
      title: 'Imports',
      key: 'imports',
    },
    {
      title: 'Exports',
      key: 'exports',
    },
  ]

  const sourceData = JSON.parse(
    document.getElementById('market-trends-data').textContent
  )

  const years = sourceData.map((x) => {
    return x.year
  })

  const data = lines.map((line) => {
    return {
      name: line.title,
      x: years,
      y: sourceData.map((x) => {
        return x[line.key]
      }),
      type: 'scatter',
      hovertemplate: `${line.title} in %{x}: £%{y}<extra></extra>`,
    }
  })

  Plotly.newPlot('plotly-market-trends', data, layout, config)
}

window.addEventListener('DOMContentLoaded', initTradeChart)
