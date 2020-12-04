import React, { memo } from 'react'

import { Input } from '@src/components/Form/Input'

export const AveragePrice = memo(() => {
  return (
    <Input
      onChange={() => {}}
      id='asdasd'
      label='test'
      hideLabel
      type='number'
      prepend='GBP'
      description='<h2 class="h-xs p-t-xs p-b-0">Average price per unit in the Netherlands</h2><p class="m-t-xs">To find the average price for your product in your target market you will have to do some research using:</p><ul class="list-dot"><li>online retailers</li><li>web searches</li><li>supermarket prices</li></ul><p class="m-b-0">These will give you a good idea of prices in your target market.</p>'
      tooltip='adasda sda asd'
    />
  )
})
