import React from 'react'

import { Input } from '@src/components/Form/Input'

export const NetPrice = () => {
  return (
    <div>
      <h2 className='h-xs p-t-l p-b-0'>Your net price per unit in the Netherlands</h2>
      <p>Deciding on what price your product will be sold for in retailers can be a difficult decision.</p>
      <p>You want to make sure you sell your product for more than it cost to make it, this way you make a profit on every unit sold.</p>

      <div className='form-group-example bg-blue-deep-10 p-xs m-b-xs'>
        <h2 className='h-xs p-t-0 p-b-0'>A fictional example to help you complete this section</h2>
        <p>To decide a final price for Dove gin we thought about:</p>
        <ul>
          <li>how much it cost to make one bottle of our gin</li>
          <li>the average price for a bottle of gin in Australia</li>
        </ul>
        <p>This helped us decide where our product would sit in the market.</p>
        <p>A bottle of our gin costs £15 to make, so to make a profit we had to charge over £15. Looking at Australian prices we decided on £25 a bottle in line with the market prices there. This gives us a profit margin of £10 on every unit sold.</p>
      </div>
      <Input onChange={() => {}} id='asdasd' label='test' hideLabel />
    </div>
  )
}
