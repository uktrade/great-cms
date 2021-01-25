import React, { memo } from 'react'
import PropTypes from 'prop-types'

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
    return (
      <div className="costs costs--funding bg-blue-deep-10 p-v-s">
        <table className="m-b-0">
          <tbody>
            {formFields.map(({ pk, amount, funding_option }) => (
              <Option
                key={pk}
                id={pk}
                value={amount}
                selectedOption={funding_option}
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

Option.propTypes = {
  formFields: PropTypes.arrayOf(
    PropTypes.shape({
      amount: PropTypes.number,
      companyexportplan: PropTypes.number.isRequired,
      funding_option: PropTypes.string,
      pk: PropTypes.number.isRequired,
    })
  ).isRequired,
  currency: PropTypes.string.isRequired,
  selectData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      options: PropTypes.array.isRequired,
      placeholder: PropTypes.string.isRequired,
    })
  ),
  onChange: PropTypes.func.isRequired,
  deleteFunding: PropTypes.func.isRequired,
  addFunding: PropTypes.func.isRequired,
}
