import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import { Select } from '@src/components/Form/Select'

export const Units = memo(({
  update,
  input,
  select
}) => {
  return (
    <>
      <h2 className='h-m p-b-xs p-t-m'>Total costs and price</h2>
      <p>Now you have calculated your direct and overhead costs, you can calculate your final cost per unit. This can be tricky but don't worry, we will tell you what you need to do.</p>
      <p className='g-panel'>You can enter up to 10 digits long value in each row in the table below.</p>
      <h2 className='h-xs p-t-0 p-b-0'>Number of units you want to export</h2>
      <p className='m-t-xs'>The first thing you can do is record how many units of your product you want to export in the following tool.</p>
      <p>Try to be as accurate as possible, this will help make your plan stronger.</p>
      <div className='grid'>
        <div className='w-full'>
          <div className='c-1-6 m-r-xs'>
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
          <div className='c-1-3'>
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
  update: PropTypes.func.isRequired
}
