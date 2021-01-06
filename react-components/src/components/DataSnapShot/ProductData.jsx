import React, { memo } from 'react'
import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import PropTypes from 'prop-types'

export const ProductData = memo(({ world, local, country }) => (
  <>
    <div className="stat-group">
      <div className="grid">
        <div className="c-1-3">
          <Stats
            header={`Total product import value in ${world.year} (USD)`}
            data={world.trade_value ? world.trade_value : notAvailable}
          />
        </div>
        <div className="c-1-3">
          <Stats
            header={`Total product import value from the UK in ${local.year} (USD)`}
            data={local.trade_value ? local.trade_value : notAvailable}
          />
        </div>
        <div className="c-1-3">
          <Stats
            header="Year-to-year product import value change"
            data={
              world.year_on_year_change
                ? world.year_on_year_change
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
              country.gdp_per_capita.year_2019
                ? country.gdp_per_capita.year_2019
                : notAvailable
            }
          />
        </div>
        <div className="c-1-2">
          <Stats header="Avg income (USD)" data={notAvailable} />
        </div>
      </div>
    </div>
    <hr className="hr bg-blue-deep-20 m-t-0" />
  </>
))

ProductData.propTypes = {
  world: PropTypes.shape({
    year: PropTypes.string,
    trade_value: PropTypes.string,
    year_on_year_change: PropTypes.string,
  }).isRequired,
  local: PropTypes.shape({
    year: PropTypes.string,
    trade_value: PropTypes.string,
  }).isRequired,
  country: PropTypes.shape({
    gdp_per_capita: PropTypes.shape({
      year_2019: PropTypes.string,
    }),
  }),
}

ProductData.defaultProps = {
  country: {
    gdp_per_capita: {
      year_2019: '',
    },
  },
}
