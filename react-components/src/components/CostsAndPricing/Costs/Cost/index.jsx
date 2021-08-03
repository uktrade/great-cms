import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import { Tooltip } from '@components/tooltip/Tooltip'

export const Cost = memo(
  ({ label, id, currency, placeholder, tooltip, value, update, type }) => {
    return (
      <div className="costs__option costs__option--border">
        <div className="costs__flex-row">
          <div className="costs__label">
            <label className="body-l-b" htmlFor={id}>
              {label}
            </label>
            {tooltip.content && <Tooltip {...tooltip} />}
          </div>
          <div className="costs__input">
            <Input
              label={label}
              id={id}
              hideLabel
              type={type}
              prepend={currency}
              value={value}
              onChange={(field) => update(field)}
              placeholder={placeholder}
              formGroupClassName="m-b-0"
            />
          </div>
        </div>
      </div>
    )
  }
)

Cost.propTypes = {
  label: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  placeholder: PropTypes.string.isRequired,
  tooltip: PropTypes.objectOf(PropTypes.string),
  value: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  update: PropTypes.func.isRequired,
}

Cost.defaultProps = {
  tooltip: '',
}
