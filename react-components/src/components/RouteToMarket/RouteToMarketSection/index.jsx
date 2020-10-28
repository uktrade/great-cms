import React from 'react'
import PropTypes from 'prop-types'

import { Select } from '@src/components/Form/Select'
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
    <div className='form-table bg-blue-deep-10 radius p-h-s p-b-xxs m-b-s' key={field.pk}>
      <button type='button' className='button--only-icon button--small button--delete text-blue-deep-40' onClick={() => deleteTable(field.pk)}>
        <i className='fas fa-trash-alt' />
      </button>
      {data.map((item) => (
        <>
          <Select
            key={item.name}
            label={item.label}
            update={(x) => update(field.pk, x)}
            name={item.name}
            options={item.options}
            selected={field[item.name] ? item.options.find(x => x.value === field[item.name]).label : ''}
          />
          <hr className='hr hr--light' />
        </>
      ))}
      <TextArea
        label={label}
        example={example}
        onChange={(e) => update(field.pk, e)}
        value={field[name]}
        id={name}
      />
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
