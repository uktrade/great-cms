import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { Option } from './Option'

export const Options = memo(
  ({ formFields, currency, selectData, onChange, deleteFunding }) => {
    // debugger
    return (
      <div className="costs bg-blue-deep-10">
        <table className="m-b-0">
          <tbody>
            {formFields.map(({ pk, value }) => (
              <Option
                key={pk}
                id={pk}
                value={value}
                currency={currency}
                selectData={selectData}
                onChange={onChange}
                deleteFunding={deleteFunding}
              />
            ))}
          </tbody>
        </table>
      </div>
    )
  }
)

// Option.propTypes = {
//   costs: PropTypes.arrayOf(PropTypes.shape({
//     label: PropTypes.string.isRequired,
//     id: PropTypes.string.isRequired,
//     placeholder: PropTypes.string.isRequired,
//     tooltip: PropTypes.string.isRequired,
//     type: PropTypes.string.isRequired,
//   })).isRequired,
//   currency: PropTypes.string.isRequired,
//   data: PropTypes.objectOf(PropTypes.number).isRequired,
//   update: PropTypes.func.isRequired,
// }
