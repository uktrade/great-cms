import React, { memo, useEffect, useState } from 'react'
import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import PropTypes from 'prop-types'
import { millify, normaliseValues, numberWithSign, get } from '@src/Helpers'

import Services from '@src/Services'

export const ProductData = ({ country, product }) => {

  const [data, setData] = useState()

 useEffect(() => {
      Services.getCountryData(
      [country],
      JSON.stringify([
        {model:'GDPPerCapita', latest:true},
        {model:'Income', latest:true},
        {model:'ComtradeReport', filter:{'commodity_code':product.commodity_code}},
      ]))
        .then((result) => {
          const out = result && result[country.country_iso2_code] || {}
          out['comTrade'] = out['ComtradeReport']
            .sort((rowa, rowb) => rowa.year>rowb.year ? -1 : 1 )
            .reduce((acc, row) => {
              const out = {...acc}
              const type = row.uk_or_world
              if(!out[type]) {
                out[type] = row
              } else {
                if (!out[type].change) {
                  out[type].change = 100*(out[type].trade_value - row.trade_value)/row.trade_value
                  out[type].last_year = row.year
                }
              }
              return out
            }, {})
          setData(out)
        })
        .catch((error) => console.log(error))
  }, [product, country])

  return data ? (<>
    <div className="stat-group">
      <div className="grid">
        <div className="c-1-3">
          <Stats
            header={`${product.commodity_name} import value in ${get(data,'comTrade.WLD.year')} (USD)`}
            data={
              get(data,'comTrade.WLD.trade_value')
                ? millify(get(data,'comTrade.WLD.trade_value'))
                : notAvailable
            }
          />
        </div>
        <div className="c-1-3">
          <Stats
            header={`${product.commodity_name} import value from the UK in ${get(data,'comTrade.GBR.year')} (USD)`}
            data={
              get(data,'comTrade.GBR.trade_value') ? millify(get(data,'comTrade.GBR.trade_value')) : notAvailable
            }
          />
        </div>
        <div className="c-1-3">
          <Stats
            header="Year-to-year product import value change"
            data={
              get(data,'comTrade.WLD.change')
                ? `${numberWithSign(
                    normaliseValues(get(data,'comTrade.WLD.change'))
                  )}% <span class="body-m">vs ${get(data,'comTrade.WLD.last_year')}</span>`
                : notAvailable
            }
          />
        </div>
      </div>
    </div>

    <div className="stat-group m-b-s-s">
      <div className="grid">
        <div className="c-1-2">
          <Stats
            header="GDP per capita (USD)"
            data={
              data.GDPPerCapita &&
              data.GDPPerCapita[0] &&
              data.GDPPerCapita[0].year_2019
                ? millify(data.GDPPerCapita[0].year_2019)
                : notAvailable
            }
          />
        </div>
        <div className="c-1-2">
          <Stats
            header="Adjusted net national income per capita (USD)"
            data={
              data.Income && data.Income[0] && data.Income[0].value
                ? millify(data.Income[0].value)
                : notAvailable
            }
          />
        </div>
      </div>
    </div>
    <hr className="hr bg-blue-deep-20 m-t-0" />
  </>) : ''
}

ProductData.propTypes = {
  product: PropTypes.shape({
    commodity_name: PropTypes.string,
  }).isRequired,
  country: PropTypes.shape({
    commodity_iso2_code: PropTypes.string,
  }).isRequired,
}
