import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const GrossPrice = memo(({
  country,
  countryGrossUnit,
  currencyGrossUnit,
  profitPerUnit,
  potentialPerUnit,
}) => (
  <>
    <div className='grid m-b-s'>
      <div className='c-1-2'>
        <div className='bg-white radius p-s'>
          <i className='fas fa-exchange-alt text-blue-deep-60 fa-lg' />
          <p className='m-t-xxs m-b-0'>Gross price per unit for the {country}</p>
          <h3 className='h-s p-t-xs p-b-0'>{countryGrossUnit}</h3>
        </div>
      </div>
      <div className='c-1-2'>
        <div className='bg-white radius p-s'>
          <i className='fas fa-tag text-blue-deep-60 fa-lg' />
          <p className='m-t-xxs m-b-0'>Gross price per unit in invoicing currency</p>
          <h3 className='h-s p-t-xs p-b-0'>{currencyGrossUnit}</h3>
        </div>
      </div>
    </div>
    <div className='grid'>
      <div className='c-1-2'>
        <div className='bg-white radius p-s'>
          <i className='fas fa-pound-sign text-blue-deep-60 fa-lg' />
          <p className='m-t-xxs m-b-0'>Your profit per unit</p>
          <h3 className='h-s p-t-xs p-b-0'>{profitPerUnit}</h3>
        </div>
      </div>
      <div className='c-1-2'>
        <div className='bg-white radius p-s'>
          <i className='fas fa-pound-sign text-blue-deep-60 fa-lg' />
          <p className='m-t-xxs m-b-0'>Your potential per unit</p>
          <h3 className='h-s p-t-xs p-b-0'>{potentialPerUnit}</h3>
        </div>
      </div>
    </div>
  </>
))

GrossPrice.propTypes = {
  country: PropTypes.string.isRequired,
  countryGrossUnit: PropTypes.string.isRequired,
  currencyGrossUnit: PropTypes.string.isRequired,
  profitPerUnit: PropTypes.string.isRequired,
  potentialPerUnit: PropTypes.string.isRequired
}


