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
              onChange={update}
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
              update={(item) => update(select.id, item)}
              name={select.name}
              options={select.options}
              selected={select.value}
              hideLabel
              placeholder={select.placeholder}
            />
          </div>
        </div>
      </div>
    </>
  )
})

Units.propTypes = {
  input: PropTypes.shape({
    label: PropTypes.string,
    id: PropTypes.string,
    value: PropTypes.string,
    type: PropTypes.string,
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
