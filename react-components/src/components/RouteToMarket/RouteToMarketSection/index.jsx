import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Select } from '@src/components/Form/Select'
import { TextArea } from '@src/components/Form/TextArea'

export const RouteToMarketSection = memo(
  ({ data, label, example, name, onChange, deleteTable, field, tooltip }) => {
    return (
      <div className="form-table bg-blue-deep-10 radius p-h-s p-b-xxs m-b-s">
        {data.map((item) => (
          <div key={`${item.name}-${field.pk}`}>
            <Select
              label={item.label}
              update={(x) => onChange(field.pk, x)}
              name={item.name}
              id={`${item.name}-${field.pk}`}
              options={item.options}
              tooltip={tooltip}
              selected={
                field[item.name] &&
                item.options.find((x) => x.value === field[item.name])
                  ? item.options.find((x) => x.value === field[item.name]).label
                  : ''
              }
            />
            <hr className="hr hr--light" />
          </div>
        ))}
        <TextArea
          label={label}
          example={example}
          onChange={(e) => onChange(field.pk, e)}
          value={field[name]}
          id={name}
          tooltip={tooltip}
        />
        <div className="text-center">
          <hr className="hr hr--light" />
          <button
            type="button"
            className="button--only-icon button button--small button--delete bg-white m-v-xs"
            onClick={() => deleteTable(field.pk)}
          >
            <i className="fas fa-trash-alt" />
          </button>
        </div>
      </div>
    )
  }
)

RouteToMarketSection.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      label: PropTypes.string,
      options: PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.string,
          label: PropTypes.string,
        })
      ).isRequired,
    }).isRequired
  ).isRequired,
  label: PropTypes.string.isRequired,
  example: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  tooltip: PropTypes.string.isRequired,
  field: PropTypes.objectOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number])
  ).isRequired,
  onChange: PropTypes.func.isRequired,
  deleteTable: PropTypes.func.isRequired,
}
