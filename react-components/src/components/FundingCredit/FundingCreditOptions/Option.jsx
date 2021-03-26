import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'

export const Option = memo(
  ({
    id,
    value,
    currency,
    selectData,
    onChange,
    deleteFunding,
    selectedOption,
  }) => {
    return (
      <>
        <tr className="border-none">
          <td>
            <Select
              id={id + selectData.name}
              options={selectData.options}
              label={selectData.name}
              name={selectData.name}
              placeholder={selectData.placeholder}
              selected={
                selectedOption &&
                selectData.options.find((x) => x.value === selectedOption)
                  ? selectData.options.find((x) => x.value === selectedOption)
                      .label
                  : ''
              }
              hideLabel
              className="m-b-0"
              update={(x) => onChange('select', id, x)}
            />
          </td>
          <td>
            <Input
              id={id}
              type="number"
              hideLabel
              label={selectData.name}
              value={value}
              prepend={currency}
              onChange={(e) => onChange('input', id, e)}
              formGroupClassName="m-b-0"
            />
          </td>
        </tr>
        <tr>
          <td className="text-center" colSpan="2">
            <ConfirmModal
              hasData={!!selectedOption || !!value}
              deleteItem={() => deleteFunding(id)}
            />
          </td>
        </tr>
      </>
    )
  }
)

Option.propTypes = {
  id: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
  currency: PropTypes.string.isRequired,
  selectData: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    options: PropTypes.array.isRequired,
    placeholder: PropTypes.string.isRequired,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  deleteFunding: PropTypes.func.isRequired,
}
