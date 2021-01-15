import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'

export const Option = memo(({ id, value, currency, selectData }) => {
  // debugger
  return (
    <>
      <tr>
        <td>
          <Select
            id={id}
            options={selectData.options}
            label={selectData.name}
            hideLabel
            className="m-b-0"
          />
        </td>
        <td>
          <Input
            id={id}
            type="number"
            value={value}
            prepend={currency}
            formGroupClassName="m-b-0"
          />
        </td>
      </tr>
      <tr>
        <td>
          <button
            type="button"
            title="Click to delete this funding option and its data."
            className="button button--delete button--small button--only-icon button--tertiary"
          >
            <i className="fas fa-trash-alt"></i>
          </button>
        </td>
      </tr>
    </>
  )
})

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
