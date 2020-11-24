import React, { memo } from 'react'

import { Input } from '@src/components/Form/Input'

export const AveragePrice = memo(() => {
  return (
    <>
      <h2 className='h-xs p-t-l p-b-0'>Average price per unit in the Netherlands</h2>
      <p>To find the average price for your product in your target market you will have to do some research using:</p>
      <ul className='list-dot'>
        <li>online retailers</li>
        <li>web searches</li>
        <li>supermarket prices</li>
      </ul>

      <p className='m-b-0'>These will give you a good idea of prices in your target market.</p>
      <Input onChange={() => {}} id='asdasd' label='test' hideLabel />
    </>
  )
})
