import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { FormGroup } from '../FormGroup'

export const Checkbox = memo(
  ({ id, label, checked, onChange, errors, description, tooltip, disabled, formGroupClassName }) => {
    const handleChange = (e) => {
      onChange(e.target.checked)
    }

    return (
      <FormGroup
        errors={errors}
        description={description}
        tooltip={tooltip}
        id={id}
        formGroupClassName={formGroupClassName}
      >
        <div className="govuk-checkboxes">
          <div className="govuk-checkboxes__item">
            <input
              className="govuk-checkboxes__input"
              id={id}
              name={id}
              type="checkbox"
              disabled={disabled}
              checked={checked}
              onChange={handleChange}
            />
            <label className="govuk-label govuk-checkboxes__label" htmlFor={id}>
              {label}
            </label>
          </div>
        </div>
      </FormGroup>
    )
  }
)

Checkbox.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.node.isRequired,
  checked: PropTypes.bool.isRequired,
  onChange: PropTypes.func.isRequired,
  errors: PropTypes.arrayOf(PropTypes.string),
  description: PropTypes.string,
  tooltip: PropTypes.shape({
    title: PropTypes.string,
    content: PropTypes.string,
  }),
  disabled: PropTypes.bool,
  formGroupClassName: PropTypes.string,
}

Checkbox.defaultProps = {
  errors: [],
  description: '',
  tooltip: null,
  disabled: false,
  formGroupClassName: '',
}

export default Checkbox
