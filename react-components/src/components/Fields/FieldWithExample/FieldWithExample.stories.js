import React from 'react'
import FieldWithExample from '.'
import props from './FieldWithExample.fixtures'

export default { title: 'FieldWithExample' }

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
