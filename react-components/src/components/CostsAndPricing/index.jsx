import React, { memo } from 'react'
import { Direct } from './Direct'
import { Overhead } from './Overhead'
import { Units } from './Units'

export const CostsAndPricing = memo(({
  currency,
  direct,
  overhead
}) => {
  return (
    <>
      <Direct {...direct} currency={currency} />
      <Overhead {...overhead} currency={currency} />
      <Units />
    </>
  )
})

