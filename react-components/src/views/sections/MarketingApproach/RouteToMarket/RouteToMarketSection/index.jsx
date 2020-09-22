import React from 'react'
import PropTypes from 'prop-types'

import { InputWithDropdown } from '@src/components/Fields/InputWithDropdown'
import { TextArea } from '@src/components/Form/TextArea'

export const RouteToMarketSection = ({
  data,
  label,
  example,
  name,
  update,
  deleteTable,
  field
}) => {
  return (
    <div className='route-to-market__table' key={field.pk}>
      <button type='button' onClick={() => deleteTable(field.pk)} className='button--stone route-to-market__delete'>x</button>
      {data.map((item) => (
        <InputWithDropdown
          key={item.name}
          label={item.label}
          update={(x) => update(field.pk, x)}
          name={item.name}
          options={item.options}
          selected={field[item.name] ? item.options.find(x => x.value === field[item.name]).label : ''}
        />
      ))}
      <div className='route-to-market__table-cell'>
        <TextArea
          label={label}
          example={example}
          onChange={(e) => update(field.pk, e)}
          value={field[name]}
          id={name}
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
  field: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]).isRequired,
  update: PropTypes.func.isRequired,
  deleteTable: PropTypes.func.isRequired,
}
