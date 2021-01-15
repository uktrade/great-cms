import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'

export const Option = memo(
  ({ remove, id, currency, placeholder, value, update, type }) => {
    return (
      <>
        <tr>
          <td>
            <Select />
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
        <tr>
          <button
            type="button"
            className="button button--secondary"
            onClick={remove}
          >
            Delete
          </button>
        </tr>
      </>
    )
  }
)

// Option.propTypes = {
//   label: PropTypes.string.isRequired,
//   id: PropTypes.string.isRequired,
//   currency: PropTypes.string.isRequired,
//   placeholder: PropTypes.string.isRequired,
//   tooltip: PropTypes.string,
//   value: PropTypes.string.isRequired,
//   type: PropTypes.string.isRequired,
//   update: PropTypes.func.isRequired,
// }

// Option.defaultProps = {
//   tooltip: '',
// }
