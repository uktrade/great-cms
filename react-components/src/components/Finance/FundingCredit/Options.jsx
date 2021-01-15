import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { Option } from './Option'

export const Options = memo(({ formFields, currency, selectData }) => {
  // debugger
  return (
    <div className="costs bg-blue-deep-10">
      <table className="m-b-0">
        <tbody>
          {formFields.map(({ id, value }) => (
            <Option
              key={id}
              id={id}
              value={value}
              currency={currency}
              selectData={selectData}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
})

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
