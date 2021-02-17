import React, { memo, useState } from 'react'
import PropTypes, { shape } from 'prop-types'
import { useUpdateExportPlan } from '@src/components/hooks/useUpdateExportPlan/useUpdateExportPlan'
import { TextArea } from '@src/components/Form/TextArea'

export const VisaInformation = memo(
  ({ formData, formFields, name, field, travel_advice_link }) => {
    const [state, setState] = useState(formData)
    const [needVisa, setNeedVisa] = useState(
      Boolean(formData.visa_required) || false
    )
    const [update] = useUpdateExportPlan(field)

    const onNeedVisaChange = (event) => {
      const value = event.target.value === 'true' ? true : false
      const visaRequired = {
        [field]: { [name]: { visa_required: value } },
      }
      setNeedVisa(value)
      update(visaRequired)
    }

    const onChange = (value, data) => {
      setState({
        ...state,
        ...data,
      })
      update(value)
    }

    return (
      <div className="m-b-s">
        <h2 className="h-s m-b-xs">Visa information</h2>
        <p>
          Find out if you need a visa for your trip using gov.uk{' '}
          <a
            href={travel_advice_link}
            target="_blank"
            rel="noopener noreferrer"
          >
            Foreign Travel Advice
          </a>{' '}
          service. If you do, you'll be able to add the details here.
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
            {formFields.map((item, index) => {
              return (
                <TextArea
                  key={index}
                  {...item}
                  onChange={(data) => {
                    onChange({ [field]: { [name]: data } }, data)
                  }}
                  value={state[item.name] ? state[item.name] : ''}
                />
              )
            })}
          </div>
        )}
      </div>
    )
  }
)

VisaInformation.propTypes = {
  formData: PropTypes.shape({
    how_long: PropTypes.string,
    how_where_visa: PropTypes.string,
    notes: PropTypes.string,
    visa_required: PropTypes.bool,
  }).isRequired,
  formFields: PropTypes.arrayOf(
    PropTypes.shape({
      field_type: PropTypes.string,
      id: PropTypes.string,
      label: PropTypes.string,
      name: PropTypes.string,
      placeholder: PropTypes.string,
    })
  ).isRequired,
  name: PropTypes.string.isRequired,
  field: PropTypes.string.isRequired,
  travel_advice_link: PropTypes.string.isRequired,
}
