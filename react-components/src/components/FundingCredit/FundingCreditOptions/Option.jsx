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
      <div className="costs__option costs__option--border">
        <div className="grid">
          <div className="c-7-12">
            <Select
              id={id + selectData.name}
              options={selectData.options}
              label={selectData.name}
              name={selectData.name}
              placeholder={selectData.placeholder}
              selected={selectedOption}
              hideLabel
              className="m-b-xs"
              update={(x) => onChange('select', id, x)}
            />
          </div>
          <div className="c-5-12">
            <Input
              id={id}
              type="number"
              decimal={0}
              hideLabel
              label={selectData.name}
              placeholder={0}
              value={value}
              prepend={currency}
              onChange={(e) => onChange('input', id, e)}
              formGroupClassName="m-b-xs"
            />
          </div>
          <div className="c-full text-center">
            <ConfirmModal
              hasData={!!selectedOption || !!value}
              deleteItem={() => deleteFunding(id)}
            />
          </div>
        </div>
      </div>
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
