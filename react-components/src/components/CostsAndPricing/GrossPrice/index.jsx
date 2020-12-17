import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'
import { Tooltip } from '@components/tooltip/Tooltip'

export const GrossPrice = memo(
  ({
    country,
    currency,
    GrossPriceUnit,
    profitPerUnit,
    potentialPerUnit,
    update,
    input,
    select,
  }) => (
    <>
      <div className="bg-white radius p-xs c-full m-b-s gross-price">
        <div className="">
          <i className="fas fa-tag text-blue-deep-60 fa-lg" />
          <p className="m-t-xxs m-b-0">
            Gross price per unit for the {country}
          </p>
          <h3 className="h-s p-t-0 p-b-0">
            {currency} {GrossPriceUnit}
          </h3>
        </div>
        <hr className="hr--light m-v-xs" />
        <div className="">
          <p className="m-t-xxs m-b-0">
            Gross price per unit in invoicing currency
          </p>
          <Tooltip content="asdasdad" />
          <div className="grid m-t-xs">
            <div className="w-full">
              <div className="c-1-6 m-r-xs">
                <Select
                  label={select.label}
                  update={(item) => update(select.id, item)}
                  name={select.name}
                  options={select.options}
                  selected={select.value}
                  hideLabel
                  placeholder={select.placeholder}
                />
              </div>
              <div className="c-1-3">
                <Input
                  onChange={update}
                  label={input.label}
                  id={input.id}
                  hideLabel
                  type={input.type}
                  value={input.value}
                  placeholder={input.placeholder}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="grid">
        <div className="c-1-2 m-b-s">
          <div className="bg-white radius p-xs">
            <i className="fas fa-pound-sign text-blue-deep-60 fa-lg" />
            <p className="m-t-xxs m-b-0">Your profit per unit</p>
            <h3 className="h-s p-t-0 p-b-0">
              {currency} {profitPerUnit}
            </h3>
          </div>
        </div>
        <div className="c-1-2 m-b-s">
          <div className="bg-white radius p-xs">
            <i className="fas fa-pound-sign text-blue-deep-60 fa-lg" />
            <p className="m-t-xxs m-b-0">Your potential per unit</p>
            <h3 className="h-s p-t-0 p-b-0">
              {currency} {potentialPerUnit}
            </h3>
          </div>
        </div>
      </div>
    </>
  )
)

GrossPrice.propTypes = {
  country: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  GrossPriceUnit: PropTypes.string.isRequired,
  profitPerUnit: PropTypes.string.isRequired,
  potentialPerUnit: PropTypes.string.isRequired,
  update: PropTypes.func.isRequired,
  input: PropTypes.shape({
    label: PropTypes.string,
    id: PropTypes.string,
    value: PropTypes.string,
    placeholder: PropTypes.string,
    type: PropTypes.string,
  }).isRequired,
  select: PropTypes.shape({
    label: PropTypes.string,
    id: PropTypes.string,
    name: PropTypes.string,
    value: PropTypes.string,
    placeholder: PropTypes.string,
    options: PropTypes.arrayOf({
      value: PropTypes.string,
      label: PropTypes.string,
    }).isRequired,
  }).isRequired,
}
