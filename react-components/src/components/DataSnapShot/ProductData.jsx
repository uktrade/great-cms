import React, { memo } from 'react'
import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import PropTypes from 'prop-types'
import { millify, normaliseValues, numberWithSign } from '@src/Helpers'

export const ProductData = memo(({ world, local, country, product }) => (
  <>
    <div className="stat-group">
      <div className="grid">
        <div className="c-1-3">
          <Stats
            header={`${product.commodity_name} import value in ${world.year} (USD)`}
            data={
              world.trade_value_raw
                ? millify(world.trade_value_raw)
                : notAvailable
            }
          />
        </div>
        <div className="c-1-3">
          <Stats
            header={`${product.commodity_name} import value from the UK in ${local.year} (USD)`}
            data={
              local.trade_value_raw
                ? millify(local.trade_value_raw)
                : notAvailable
            }
          />
        </div>
        <div className="c-1-3">
          <Stats
            header="Year-to-year product import value change"
            data={
              world.year_on_year_change
                ? `${numberWithSign(
                    normaliseValues(world.year_on_year_change)
                  )}% <span class="body-m">vs ${world.last_year}</span>`
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
              country.GDPPerCapita &&
              country.GDPPerCapita[0] &&
              country.GDPPerCapita[0].year_2019
                ? millify(country.GDPPerCapita[0].year_2019)
                : notAvailable
            }
          />
        </div>
        <div className="c-1-2">
          <Stats
            header="Adjusted net national income per capita (USD)"
            data={
              country.Income && country.Income[0] && country.Income[0].value
                ? millify(country.Income[0].value)
                : notAvailable
            }
          />
        </div>
      </div>
    </div>
    <hr className="hr bg-blue-deep-20 m-t-0" />
  </>
))

ProductData.propTypes = {
  product: PropTypes.shape({
    commodity_name: PropTypes.string,
  }).isRequired,
  world: PropTypes.shape({
    year: PropTypes.int,
    trade_value_raw: PropTypes.int,
    year_on_year_change: PropTypes.number,
    last_year: PropTypes.int,
  }).isRequired,
  local: PropTypes.shape({
    year: PropTypes.int,
    trade_value_raw: PropTypes.int,
  }).isRequired,
  country: PropTypes.shape({
    GDPPerCapita: PropTypes.arrayOf(
      PropTypes.shape({
        year_2019: PropTypes.string,
      })
    ),
    Income: PropTypes.arrayOf(
      PropTypes.shape({
        value: PropTypes.string,
      })
    ).isRequired,
  }),
}

ProductData.defaultProps = {
  country: {
    gdp_per_capita: {
      year_2019: '',
    },
  },
}
