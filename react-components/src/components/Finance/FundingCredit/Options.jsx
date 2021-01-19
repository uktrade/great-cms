import React, { memo } from 'react'
// import PropTypes from 'prop-types'

import { Option } from './Option'

export const Options = memo(
  ({
    formFields,
    currency,
    selectData,
    onChange,
    deleteFunding,
    addFunding,
  }) => {
    // debugger
    return (
      <div className="costs costs--funding bg-blue-deep-10 p-v-s">
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
          <tfoot>
            <tr>
              <td colSpan="2">
                <button
                  type="button"
                  className="button button--secondary button--icon button--small button--add"
                  onClick={addFunding}
                >
                  <i className="fas fa-plus-circle"></i>
                  <span>Add a funding option</span>
                </button>
              </td>
            </tr>
          </tfoot>
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
