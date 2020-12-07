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
import { direct, overhead} from './constants'

export const CostsAndPricing = memo(({
  currency,
  country,
  data,
  update
}) => {
  return (
    <>
      <section className='container'>
        <div className='grid'>
          <div className='c-1-4'>&nbsp;</div>
          <div className='c-1-2'>
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
            <Units />
            <FinalCost />
            <AveragePrice country={country} />
            <NetPrice country={country} />
            <LocalTaxes country={country} />
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
                country={country}
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

