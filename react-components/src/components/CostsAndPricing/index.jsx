import React, { memo } from 'react'
import { Direct } from './Direct'
import { Overhead } from './Overhead'
import { Units } from './Units'
import { FinalCost } from './FinalCost'
import { AveragePrice } from './AveragePrice'
import { NetPrice } from './NetPrice'
import { LocalTaxes } from './LocalTaxes'
import { Duty } from './Duty'
import { GrossPrice } from './GrossPrice'

export const CostsAndPricing = memo(({
  currency,
  direct,
  overhead
}) => {
  return (
    <>
      <section className='container'>
        <div className='grid'>
          <div className='c-1-4'>&nbsp;</div>
          <div className='c-1-2'>
            <Direct {...direct} currency={currency} />
            <Overhead {...overhead} currency={currency} />
            <Units />
            <FinalCost />
            <AveragePrice />
            <NetPrice />
            <LocalTaxes />
            <Duty />
          </div>
          <div className='c-1-4'>&nbsp;</div>
        </div>
      </section>
      <section className='bg-blue-deep-10 m-t-l p-v-s'>
        <div className='container'>
          <div className='grid'>
            <div className='c-1-4 p-0'>&nbsp;</div>
            <div className='c-1-2'>
              <GrossPrice
                country='Netherlands'
                countryGrossUnit='GBP 0'
                currencyGrossUnit='GBP 0'
                potentialPerUnit='GBP 0'
                profitPerUnit='GBP 0'
              />
            </div>
            <div className='c-1-4'>&nbsp;</div>
          </div>
        </div>
      </section>
    </>
  )
})

