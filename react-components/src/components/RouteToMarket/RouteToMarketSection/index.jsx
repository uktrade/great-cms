import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Select } from '@src/components/Form/Select'
import { TextArea } from '@src/components/Form/TextArea'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'

export const RouteToMarketSection = memo(
  ({ data, label, example, name, onChange, deleteTable, field, lesson }) => {
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
              selected={field[item.name]}
              lesson={item.lesson}
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
        />
        <div className="text-center">
          <hr className="hr hr--light" />
          <ConfirmModal
            hasData={!!field[name] || !!field.promote || !!field.route}
            deleteItem={() => deleteTable(field.pk)}
          />
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
  example: PropTypes.oneOfType([
    PropTypes.shape({
      buttonTitle: PropTypes.string,
      header: PropTypes.string,
      content: PropTypes.string,
    }),
    PropTypes.string,
  ]),
  name: PropTypes.string.isRequired,
  field: PropTypes.objectOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number])
  ).isRequired,
  onChange: PropTypes.func.isRequired,
  deleteTable: PropTypes.func.isRequired,
  lesson: PropTypes.objectOf(PropTypes.oneOfType([PropTypes.string])),
}

RouteToMarketSection.defaultProps = {
  lesson: {},
  example: {},
}
