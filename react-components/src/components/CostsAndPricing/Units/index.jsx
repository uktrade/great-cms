import React, { memo } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'

export const Units = memo(({ update, input, select, description }) => {
  return (
    <>
      {ReactHtmlParser(description)}
      <div className="inputgroup">
        <div className="inputgroup__input inputgroup__input--medium">
          <Input
            onChange={(x) => {
              const postData = input.field({
                unit: select.value,
                value: x[input.id],
              })

              update(x, postData)
            }}
            label={input.label}
            id={input.id}
            type={input.type}
            value={input.value}
            placeholder={input.placeholder}
            decimal={0}

          />
        </div>
        <div className="inputgroup__input inputgroup__input--medium">
          <Select
            label={select.label}
            id={select.id}
            update={(item) => {
              const postData = input.field({
                unit: item[select.name],
                value: input.value,
              })
              update({ [select.id]: item[select.name] }, postData)
            }}
            name={select.name}
            options={select.options}
            placeholder={select.placeholder}
            selected={select.value}
          />
        </div>
      </div>
    </>
  )
})

Units.propTypes = {
  description: PropTypes.string.isRequired,
  input: PropTypes.shape({
    label: PropTypes.string,
    id: PropTypes.string,
    value: PropTypes.string,
    type: PropTypes.string,
    field: PropTypes.func,
    placeholder: PropTypes.string,
  }).isRequired,
  select: PropTypes.shape({
    label: PropTypes.string,
    id: PropTypes.string,
    name: PropTypes.string,
    value: PropTypes.string,
    placeholder: PropTypes.string,
    options: PropTypes.arrayOf(
      PropTypes.shape({
        value: PropTypes.string,
        label: PropTypes.string,
      }),
    ).isRequired,
  }).isRequired,
  update: PropTypes.func.isRequired,
}
