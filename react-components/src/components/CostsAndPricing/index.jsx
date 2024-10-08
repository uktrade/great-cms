import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import { Input } from '@src/components/Form/Input'
import { formatLessonLearned, prependThe } from '@src/Helpers'

import { MonthYearInput } from '@src/components/Form/MonthYearInput'
import { Direct } from './Direct'
import { Overhead } from './Overhead'
import { GrossPrice } from './GrossPrice'
import { Units } from './Units'

export const CostsAndPricing = memo(
  ({
    currency,
    country,
    data,
    update,
    units,
    totals,
    initialData,
    currencies,
    init,
    lessonDetails,
    currentSection,
    formFields: {
      direct,
      overhead,
      costPerUnit,
      averagePrice,
      netPrice,
      localTaxes,
      duty,
      exportQuantity,
      exportUnits,
      exportEndMonth,
      exportEndYear,
      grossPriceUnitSelect,
      grossPriceCurrency,
    },
  }) => {
    useState(() => {
      init({
        ...totals,
        ...initialData,
        units,
        currencies,
      })
    }, [])

    const onChange = (updateField, input) => {
      update(updateField, {
        [input.field]: {
          [input.id]: updateField[input.id],
        },
      })
    }
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
                description={exportQuantity.description}
                update={update}
                input={{ ...exportQuantity, value: data.export_quantity }}
                select={{
                  ...exportUnits,
                  value: data.export_units,
                  options: data.units,
                }}
              />
              <MonthYearInput
                className="m-t-s"
                label={exportEndMonth.label}
                monthName={exportEndMonth.id}
                yearName={exportEndYear.id}
                monthValue={data.export_end}
                yearValue={data.export_end_year}
                onChange={(x, values) => update(x, {
                  [exportEndMonth.field]: {
                    [exportEndMonth.id]: values,
                  },
                })}
                onChangeCombineFields
              />

              {ReactHtmlParser(exportQuantity.after)}

              <Input
                onChange={(x) => onChange(x, costPerUnit)}
                value={data.final_cost_per_unit}
                hideLabel
                prepend={currency}
                {...costPerUnit}
                example={
                  data.estimated_costs_per_unit
                    ? {
                      ...costPerUnit.example,
                      header: costPerUnit.example.header(
                        `${currency} ${data.estimated_costs_per_unit}`,
                      ),
                    }
                    : {}
                }
              />
              <Input
                onChange={(x) => onChange(x, averagePrice)}
                value={data.average_price_per_unit}
                hideLabel
                prepend={currency}
                {...averagePrice}
                description={averagePrice.description(prependThe(country))}
              />
              <Input
                onChange={(x) => onChange(x, netPrice)}
                value={data.net_price}
                hideLabel
                prepend={currency}
                {...netPrice}
                description={netPrice.description(prependThe(country))}
              />
              <Input
                onChange={(x) => onChange(x, localTaxes)}
                value={data.local_tax_charges}
                hideLabel
                prepend={currency}
                {...localTaxes}
                lesson={formatLessonLearned(lessonDetails, currentSection, 0)}
                description={localTaxes.description(prependThe(country))}
              />
              <Input
                onChange={(x) => onChange(x, duty)}
                value={data.duty_per_unit}
                hideLabel
                prepend={currency}
                {...duty}
                lesson={formatLessonLearned(lessonDetails, currentSection, 1)}
              />
            </div>
            <div className="c-1-12-m c-1-4-xl">&nbsp;</div>
          </div>
        </section>
        <section className="export-plan-section-lesson">
          <div className="container">
            <div className="grid">
              <div className="c-1-4">&nbsp;</div>
              <div className="c-1-1 c-2-3-m c-1-2-xl">
                <GrossPrice
                  lesson={formatLessonLearned(lessonDetails, currentSection, 2)}
                  country={country}
                  currency={currency}
                  GrossPriceUnit={data.gross_price_per_unit}
                  potentialPerUnit={data.potential_total_profit}
                  profitPerUnit={data.profit_per_unit}
                  update={update}
                  input={{
                    ...grossPriceCurrency,
                    value: data.gross_price_per_unit_invoicing,
                  }}
                  select={{
                    ...grossPriceUnitSelect,
                    value: data.gross_price_per_unit_currency,
                    options: data.currencies,
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
  data: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
      PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.string,
          label: PropTypes.string,
        })
      ),
    ])
  ).isRequired,
  update: PropTypes.func.isRequired,
  init: PropTypes.func.isRequired,
  units: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string,
    })
  ).isRequired,
  currencies: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string,
    })
  ).isRequired,
  exportTimeframe: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string,
    })
  ).isRequired,
  totals: PropTypes.shape({
    calculated_cost_pricing: PropTypes.objectOf(PropTypes.string),
  }).isRequired,
  initialData: PropTypes.object.isRequired,
  lessonDetails: PropTypes.object.isRequired,
  currentSection: PropTypes.shape({
    url: PropTypes.string,
    lessons: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
  formFields: PropTypes.objectOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.func])
  ).isRequired,
}
