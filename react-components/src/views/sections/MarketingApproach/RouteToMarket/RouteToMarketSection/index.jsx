import React from 'react'
import PropTypes from 'prop-types'

import { InputWithDropdown } from '@src/components/Fields/InputWithDropdown'
import FieldWithExample from '@src/components/Fields/FieldWithExample'

export const RouteToMarketSection = ({
  data,
  label,
  example,
  name
}, update, i) => {
  return (
    <div className='route-to-market__table' key={i}>
      {data.map((item) => (
        <InputWithDropdown
          key={item.name}
          label={item.label}
          update={(x) => update(i, x)}
          name={item.name}
          options={item.options}
        />
      ))}
      <div className='route-to-market__table-cell'>
        <FieldWithExample
          label={label}
          example={example}
          name={name}
          handleChange={(e) => update(i, {[e.target.name]: e.target.value})}
        />
      </div>
    </div>
  )
}

RouteToMarketSection.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      label: PropTypes.string,
      options: PropTypes.arrayOf(PropTypes.string)
    }).isRequired
  ).isRequired,
  label: PropTypes.string.isRequired,
  example: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
}
