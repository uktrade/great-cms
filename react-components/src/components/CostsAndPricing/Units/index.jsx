import React, { memo } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'

export const Units = memo(({ update, input, select, description }) => {
  return (
    <>
      {ReactHtmlParser(description)}
      <div className="grid">
        <div className="w-full">
          <div className="c-1-6 m-r-xs">
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
              hideLabel
              type={input.type}
              value={input.value}
              placeholder={input.placeholder}
            />
          </div>
          <div className="c-1-3">
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
              hideLabel
              placeholder={select.placeholder}
              selected={select.value}
            />
          </div>
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
    options: PropTypes.arrayOf({
      value: PropTypes.string,
      label: PropTypes.string,
    }).isRequired,
  }).isRequired,
  update: PropTypes.func.isRequired,
}
