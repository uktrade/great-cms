import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'
import { objectHasValue } from '@src/Helpers'
import { Option } from './Option'

export const Options = memo(
  ({ formData, currency, selectData, onChange, deleteFunding, addFunding }) => {
    const { companyexportplan, pk, ...lastField } = formData.length
      ? formData[formData.length - 1]
      : {}

    return (
      <div className="costs costs--funding bg-blue-deep-10 p-v-s">
        <table className="m-b-0">
          <tbody>
            {formData.map(({ pk, amount, funding_option }) => (
              <Option
                key={pk}
                id={pk}
                value={Number(amount)}
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
                <AddButton
                  isDisabled={
                    formData.length ? !objectHasValue(lastField) : false
                  }
                  add={addFunding}
                  btnClass="button--small button--secondary button--inherit"
                  cta="Add a funding option"
                />
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    )
  }
)

Options.propTypes = {
  formData: PropTypes.arrayOf(
    PropTypes.shape({
      amount: PropTypes.number,
      companyexportplan: PropTypes.number.isRequired,
      funding_option: PropTypes.string,
      pk: PropTypes.number.isRequired,
    })
  ).isRequired,
  selectData: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    options: PropTypes.array.isRequired,
    placeholder: PropTypes.string.isRequired,
  }).isRequired,
  currency: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  deleteFunding: PropTypes.func.isRequired,
  addFunding: PropTypes.func.isRequired,
}
