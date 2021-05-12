import React from 'react'
import Services from '@src/Services'
import { normaliseValues, get, millify, numberWithSign } from '../../Helpers'

const importValueAndChange = (importValue) => {
  if (!importValue.trade_value_raw) {
    throw new Error()
  }
  return (
    <>
      <div className="body-l primary">
        {millify(importValue.trade_value_raw)}
      </div>
      {importValue.year_on_year_change && (
        <div className="body-m secondary text-black-60">
          {numberWithSign(normaliseValues(importValue.year_on_year_change))}% vs{' '}
          {importValue.last_year}
        </div>
      )}
    </>
  )
}

export default {
  tabName: 'YOUR PRODUCT',
  sourceAttributions: [
    {
      title: 'Trade data',
      linkText: 'UN Comtrade',
      linkTarget: 'https://comtrade.un.org/data',
      text: 'Copyright United Nations 2020.',
    },
  ],
  columns: {
    'world-import-value': {
      name: (context) =>
        `International import value (USD) for "${get(
          context,
          'product.commodityName'
        )}"`,
      className: 'text-align-right',
      render: (data) => importValueAndChange(data.import_from_world),
      year: (data) => get(data, 'import_from_world.year'),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>This shows how much money the selected countries and territories spent buying your product from around the world.</p>
         `,
      },
      group: 'import',
    },
    'uk-import-value': {
      name: (context) =>
        `Import value (USD) from the UK for "${get(
          context,
          'product.commodityName'
        )}"`,
      className: 'text-align-right',
      render: (data) => importValueAndChange(data.import_from_uk),
      year: (data) => get(data, 'import_from_uk.year'),
      group: 'import',
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>This shows how much money the selected countries and territories spent buying your product from around the UK.</p>
         `,
      },
    },
  },
  groups: {
    import: {
      dataFunction: Services.getComTradeData,
    },
  },
}
