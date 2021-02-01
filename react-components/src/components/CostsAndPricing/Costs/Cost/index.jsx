import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import { Tooltip } from '@components/tooltip/Tooltip'

export const Cost = memo(
  ({ label, id, currency, placeholder, tooltip, value, update, type }) => {
    return (
      <tr>
        <td>
          <label className="form-label p-b-xs" htmlFor={id}>
            {label}
          </label>
          {tooltip.content && <Tooltip {...tooltip} />}
        </td>
        <td>
          <Input
            label={label}
            id={id}
            hideLabel
            type={type}
            prepend={currency}
            value={value}
            onChange={(field) => update(field)}
            placeholder={placeholder}
          />
        </td>
      </tr>
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
