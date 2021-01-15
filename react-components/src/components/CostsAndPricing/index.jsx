import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import { Input } from '@src/components/Form/Input'

import { Direct } from './Direct'
import { Overhead } from './Overhead'
import { Units } from './Units'
import { GrossPrice } from './GrossPrice'
import {
  direct,
  overhead,
  costPerUnit,
  averagePrice,
  netPrice,
  localTaxes,
  duty,
  unitsToExport,
  exportUnits,
  grossPriceUnitSelect,
  timeframe,
  grossPriceCurrency,
} from './constants'

export const CostsAndPricing = memo(
  ({
    currency,
    country,
    data,
    update,
    units,
    exportTimeframe,
    totals,
    initialData,
    currencies,
    timeframeUnits,
    init,
  }) => {
    useState(() => {
      init({
        ...totals,
        ...initialData,
      })
    }, [])

    return (
      <>
        <section className="container">
          <div className="grid">
            <div className="c-1-4">&nbsp;</div>
            <div className="c-1-1 c-2-3-m c-1-2-xl">
              <Direct
                costs={direct}
                currency={currency}
                data={data}
                update={update}
              />
              <Overhead
                costs={overhead}
                currency={currency}
                data={data}
                update={update}
              />
              <Units
                description={
                  '<h2 class="h-m p-b-xs p-t-m">Total costs and price</h2><p>Now you have calculated your direct and overhead costs, you can calculate your final cost per unit. This can be tricky but don\'t worry, we will tell you what you need to do. </p><h2 class="h-xs p-t-0 p-b-0">Number of units you want to export</h2><p class="m-t-xs">First, record how many units you want to export over a given period of time.</p><p class="m-b-xs">The more accurate you are, the better your plan will be.</p>'
                }
                update={update}
                input={{ ...unitsToExport, value: data.units_to_export }}
                select={{
                  ...exportUnits,
                  value: data.export_units,
                  options: units,
                }}
              />
              <Units
                description={'<p class="m-t-0 m-b-xs">over the next</p>'}
                update={update}
                input={{ ...timeframe, value: data.time_frame }}
                select={{
                  ...timeframeUnits,
                  value: data.export_time_frame,
                  options: exportTimeframe,
                }}
              />
              <Input
                onChange={update}
                value={data.cost_per_unit}
                hideLabel
                prepend={currency}
                {...costPerUnit}
              />
              <Input
                onChange={update}
                value={data.average_price}
                hideLabel
                prepend={currency}
                description={`<h2 class="h-xs p-t-xs p-b-0">Average price per unit in the ${country}</h2><p class="m-t-xs">Find the average price of similar products in your target market. Do some research using:</p><ul class="list-dot"><li>online retailers</li><li>web searches</li><li>store prices</li></ul><p>Then find the average of these prices and enter the figure below.</p><p class="m-b-0">Remember to convert the figure to GBP before entering it.</p>`}
                {...averagePrice}
              />
              <Input
                onChange={update}
                value={data.net_price}
                hideLabel
                prepend={currency}
                description={`<h2 class="h-xs p-t-0 p-b-0">Your net price per unit in the ${country}</h2><p class="m-t-xs">Deciding on what price your product will be sold for in retailers can be a difficult decision.</p><p class="m-b-0">You want to make sure you sell your product for more than it cost to make it, this way you make a profit on every unit sold.</p>`}
                {...netPrice}
              />
              <Input
                onChange={update}
                value={data.local_taxes}
                hideLabel
                prepend={currency}
                description={`<h2 class="h-xs p-t-0 p-b-0">Local taxes and charges in the ${country}</h2><p class="m-t-xs">You may need to pay tax on your exports and factor this into your gross price per unit to ensure you make a profit.</p><p>To help you, we've calculated how much tax you'll pay per unit when exporting to ${country}</p>`}
                {...localTaxes}
              />
              <Input
                onChange={update}
                value={data.duty}
                hideLabel
                prepend={currency}
                {...duty}
              />
            </div>
            <div className="c-1-12-m c-1-4-xl">&nbsp;</div>
          </div>
        </section>
        <section className="bg-blue-deep-10 m-t-l p-v-s">
          <div className="container">
            <div className="grid">
              <div className="c-1-4">&nbsp;</div>
              <div className="c-1-1 c-2-3-m c-1-2-xl">
                <GrossPrice
                  country={country}
                  currency={currency}
                  GrossPriceUnit={data.gross_price_per_unit}
                  potentialPerUnit={data.potential_per_unit}
                  profitPerUnit={data.profit_per_unit}
                  update={update}
                  input={{
                    ...grossPriceCurrency,
                    value: data.gross_price_per_unit_invoicing,
                  }}
                  select={{
                    ...grossPriceUnitSelect,
                    value: data.gross_price_per_unit_currency,
                    options: currencies,
                  }}
                />
              </div>
              <div className="c-1-12-m c-1-4-xl">&nbsp;</div>
            </div>
          </div>
        </section>
      </>
    )
  }
)

CostsAndPricing.propTypes = {
  currency: PropTypes.string.isRequired,
  country: PropTypes.string.isRequired,
  data: PropTypes.oneOfType([PropTypes.string]).isRequired,
  update: PropTypes.func.isRequired,
  init: PropTypes.func.isRequired,
  units: PropTypes.arrayOf({
    value: PropTypes.string,
    label: PropTypes.string,
  }).isRequired,
  currencies: PropTypes.arrayOf({
    value: PropTypes.string,
    label: PropTypes.string,
  }).isRequired,
  exportTimeframe: PropTypes.arrayOf({
    value: PropTypes.string,
    label: PropTypes.string,
  }).isRequired,
  totals: PropTypes.oneOfType([PropTypes.string]).isRequired,
  initialData: PropTypes.oneOfType([PropTypes.string]).isRequired,
}
