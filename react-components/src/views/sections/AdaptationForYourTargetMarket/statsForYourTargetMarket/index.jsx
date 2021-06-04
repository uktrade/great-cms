import React, { memo, useEffect, useState } from 'react'
import PropTypes from 'prop-types'

import { Tooltip } from '@components/tooltip/Tooltip'
import { ToggleSnapshot } from '@src/components/ToggleSnapshot'
import { Stats } from '@src/components/Stats'
import { notAvailable } from '@src/components/Stats/StatsGroup'
import { formatLanguages } from '@src/components/TargetAgeGroupInsights/utils'
import Services from '@src/Services'
import { useSelector, Provider } from 'react-redux'
import { getMarkets, getProducts } from '@src/reducers'
import { get } from '@src/Helpers'

export const DataSnapshot = memo(({ infoMoment, tooltip }) => {
  const country = useSelector((state) => getMarkets(state))
  const product = useSelector((state) => getProducts(state))
  const [data, setData] = useState({})

  const getCountryData = () => {
    Services.getCountryData(
      [country],
      [JSON.stringify([{ model: 'CIAFactbook', latest: true }])]
    )
      .then((result) => {
        setData((result || {})[country.country_iso2_code])
      })
      .catch((error) => console.log(error))
  }

  useEffect(() => {
    getCountryData()
  }, [country, product])

  const showLanguages = () => {
    const languages = get(data, 'CIAFactbook.0.languages.language')
    return languages ? formatLanguages(languages) : notAvailable
  }

  return (
    <>
      <h2 className="h-xs p-t-l p-b-s">
        Data Snapshot: exporting {product.commodity_name} to{' '}
        {country.country_name}
      </h2>
      <ToggleSnapshot isOpen={false}>
        <div className="width-full">
          <div className="grid">
            <div className="c-full">
              <Stats
                header="The main languages in your chosen market are:"
                data={showLanguages()}
                childPosition="bottom"
              >
                {tooltip && (
                  <Tooltip
                    id="languages-in-target-market-tooltip"
                    {...tooltip}
                  />
                )}
              </Stats>
              <hr className="hr hr--light" />
              {infoMoment && (
                <Stats
                  data={infoMoment || notAvailable}
                  descriptionClassName="body-l"
                  className="statistic--mobile-full"
                >
                  <div className="fas fa-lg fa-info-circle text-blue-deep-30" aria-hidden="true" />
                </Stats>
              )}
            </div>
          </div>
        </div>
      </ToggleSnapshot>
    </>
  )
})

export const Table = memo(({ infoMoment, tooltip }) => {
  return (
    <Provider store={Services.store}>
      <DataSnapshot infoMoment={infoMoment} tooltip={tooltip} />
    </Provider>
  )
})

Table.propTypes = {
  infoMoment: PropTypes.string.isRequired,
  tooltip: PropTypes.shape({
    title: PropTypes.string,
    content: PropTypes.string.isRequired,
  }),
}

Table.defaultProps = {
  tooltip: null,
}
