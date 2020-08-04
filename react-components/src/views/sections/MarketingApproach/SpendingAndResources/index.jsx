import React from 'react'

import FieldWithExample from '@src/components/Fields/FieldWithExample'

export const SpendingAndResources = ({ data = [] }) => {
  return (
    <>
      {data.map(field => (
        <FieldWithExample
          tooltip={field.tooltip}
          label={field.label}
          example={field.example}
          key={field.name}
          name={field.name}
          value=''
          description={field.description}
          placeholder={Number.isInteger(field.placeholder) ? field.placeholder : 'Add some text'}
          currency={field.currency}
          tag={Number.isInteger(field.placeholder) ? 'number' : 'text'}
          handleChange={() => {}}
        />
      ))}
    </>
  )
}
