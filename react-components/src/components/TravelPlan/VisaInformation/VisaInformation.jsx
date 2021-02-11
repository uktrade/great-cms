import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import { FormElements } from '@src/components/FormElements'

export const VisaInformation = (params) => {
  const [needVisa, setNeedVisa] = useState(false)

  const onNeedVisaChange = (event) => {
    const value = event.target.value
    setNeedVisa(value === 'true' ? true : false)
  }

  return (
    <div className="m-b-s">
      <h2 className="h-s m-b-xs">Visa information</h2>
      <p>
        Find out if you need a visa for your trip using gov.uk{' '}
        <a href="/">Foreign Travel Advice</a> service. If you do, you'll be able
        to add the details here.
      </p>

      <div className="great-radio m-b-xs">
        <input
          id="need-visa-false"
          className="great-radio__input"
          name="need-visa-radio-group"
          type="radio"
          value="false"
          checked={needVisa === false}
          onChange={(event) => onNeedVisaChange(event)}
        />
        <label htmlFor="need-visa-false" className="great-radio__label">
          I don't need a visa
        </label>
      </div>
      <div className="great-radio">
        <input
          id="need-visa-true"
          className="great-radio__input"
          name="need-visa-radio-group"
          type="radio"
          value="true"
          checked={needVisa === true}
          onChange={(event) => onNeedVisaChange(event)}
        />
        <label htmlFor="need-visa-true" className="great-radio__label">
          I need a visa
        </label>
      </div>

      {needVisa && (
        <div className="g-panel g-panel--radio m-b-s">
          <FormElements {...params} formGroupClassName="form-group--small" />
        </div>
      )}
    </div>
  )
}
