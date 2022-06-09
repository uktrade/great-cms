// Plotly is imported in template from CDN

export const initTradeChart = (marketTrendsUnit) => {
  const config = {
    displayModeBar: false,
    responsive: true,
    locale: 'en-GB',
  }
  const layout = {
    yaxis: {
      fixedrange: true,
      rangemode: 'tozero',
      tickformat: 'gbpround',
      title: '£ ' + marketTrendsUnit,
    },
    xaxis: {
      fixedrange: true,
      showgrid: false,
      showticklabels: true,
      tickmode: 'linear',
      showspikes: true,
      spikethickness: 2,
      spikemode: 'across',
      spikelabel: false,
    },
    hovermode: 'closest',
    font: {
      family: 'Roboto, sans-serif',
      size: 18,
    },
    legend: {
      orientation: 'h',
      y: -0.25,
      xanchor: 'center',
      x: 0.5,
    },
    colorway: ['#006ccc', '#b00d23', '#00A699', '#666666'],
    margin: {
      b: 10,
      t: 10,
      r: 20,
      pad: 10,
    },
    width: document.querySelector('.tabs__nav').clientWidth,
  }

  const lines = [
    {
      title: 'Total trade',
      key: 'total',
      style: 'dash',
    },
    {
      title: 'Imports',
      key: 'imports',
      style: 'dot',
    },
    {
      title: 'Exports',
      key: 'exports',
      style: 'solid',
    },
  ]

  const sourceData = JSON.parse(
    document.getElementById('market-trends-data').textContent
  )

  const years = sourceData.map(function (x) {
    return x.year
  })

  const data = lines.map(function (line) {
    return {
      name: line.title,
      x: years,
      y: sourceData.map(function (x) {
        return line.key === 'total' ? x['imports'] + x['exports'] : x[line.key]
      }),
      mode: 'lines',
      line: {
        dash: line.style,
        width: 3,
      },
      type: 'scatter',
      hovertemplate: '%{x}: £%{y:gbp} ' + marketTrendsUnit + '<extra></extra>',
    }
  })

  const org_locale = Plotly.d3.locale
  Plotly.d3.locale = (locale) => {
    const result = org_locale(locale)
    const org_number_format = result.numberFormat
    result.numberFormat = (format) => {
      if (format === 'gbp' || format === 'gbpround') {
        const exponents = {
          trillion: 1e12,
          billion: 1e9,
          million: 1e6,
        }
        return (x) => {
          if (exponents.hasOwnProperty(marketTrendsUnit)) {
            let output = '' + x / exponents[marketTrendsUnit]
            return format === 'gbpround' || output.includes('.')
              ? output
              : output + '.0'
          }
          return '' + x
        }
      }
      return org_number_format(format)
    }
    return result
  }

  Plotly.newPlot('plotly-market-trends', data, layout, config)
}

export default {
  initTradeChart,
}
