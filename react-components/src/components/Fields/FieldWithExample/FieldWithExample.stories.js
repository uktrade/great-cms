import React from 'react'
import FieldWithExample from '.'

export default { title: 'FieldWithExample' }

const props = {
  label: 'This a the label',
  tooltip: 'This is a tooltip',
  description: 'This is a description',
  example: '<p>An example of the required text</p>',
  name: 'test'
}

export const Default = () => (
  <FieldWithExample
    {...props}
    handleChange={() => {}}
  />
)

export const NoToolTip = () => (
  <FieldWithExample
    {...props}
    tooltip=''
    handleChange={() => {}}
  />
)

export const InputOnly= () => (
  <FieldWithExample
    {...props}
    tooltip=''
    description=''
    example=''
    handleChange={() => {}}
  />
)

export const DescriptionOnly= () => (
  <FieldWithExample
    {...props}
    tooltip=''
    example=''
    handleChange={() => {}}
  />
)

export const WithNumericInputField = () => (
  <FieldWithExample
    {...props}
    tag={'number'}
    handleChange={() => {}}
  />
)

export const WithNumericInputAndCurrencyField = () => (
  <FieldWithExample
    {...props}
    tag={'number'}
    currency={'CHF'}
    handleChange={() => {}}
  />
)
