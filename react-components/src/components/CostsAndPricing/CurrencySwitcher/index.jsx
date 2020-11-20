import React from 'react'
import PropTypes from 'prop-types'

export const CurrencySwitcher = ({
  switchCurrency,
  from,
  to,
}) => (
    <button type='button' onClick={switchCurrency}>
      <i className='fas fa-exchange-alt text-red-60 m-r-xxs' /> {from} equals {to}
    </button>
)

CurrencySwitcher.propTypes = {
  switchCurrency: PropTypes.func.isRequired,
  from: PropTypes.string.isRequired,
  to: PropTypes.string.isRequired
}

