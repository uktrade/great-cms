import React, { memo } from 'react'

import { Input } from '@src/components/Form/Input'

export const FinalCost = memo(() => {
  return (
    <>
      <h2 className='h-xs p-t-0 p-b-0'>Your final cost per unit</h2>
      <p>Your final cost per unit is how much it costs your business to create one unit of your product.</p>
      <p>To work this out you will need to use 3 pieces of information you recorded earlier:</p>
      <ul className='list-dot'>
        <li>how many units of your product you want to export</li>
        <li>your direct costs final total</li>
        <li>your overhead costs final total</li>
      </ul>
      <p>You will then be able to calculate this using the tool in the next section.</p>
      <div className='form-group-example bg-blue-deep-10 p-xs m-b-xs'>
        <h2 className='h-xs p-t-0 p-b-0'>Calculation based on your values</h2>
        <p className='m-b-0 m-t-xs'>For the first step you must divide your overhead costs total by the number of units you are exporting. You must then add this total you have just worked out to your direct cost total you worked out in the table earlier.</p>
        <p className='m-b-0'>Input these into the following tool:</p>
        <p className='m-v-0'>0 + (0 / 0)</p>
      </div>
      <Input onChange={() => {}} id='asdasd' label='test' hideLabel />
    </>
  )
})

