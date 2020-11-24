import React from 'react'

import { Input } from '@src/components/Form/Input'

export const LocalTaxes = () => {
  return (
    <>
      <h2 className='h-xs p-t-l p-b-0'>Local taxes and charges in the Netherlands</h2>
      <p>Deciding on what price your product will be sold for in retailers can be a difficult decision.</p>
      <p>You want to make sure you sell your product for more than it cost to make it, this way you make a profit on every unit sold.</p>
      <div className='form-group-example bg-blue-deep-10 p-xs m-b-xs'>
        <h2 className='h-xs p-t-0 p-b-0'>List of taxes you might need to pay</h2>
        <p>Value added tax (VAT) standard rate: 21%</p>
        <p>Value added tax (VAT) reduced rate: 6%,</p>
      </div>
      <Input onChange={() => {}} id='asdasd' label='test' hideLabel />
    </>
  )
}

