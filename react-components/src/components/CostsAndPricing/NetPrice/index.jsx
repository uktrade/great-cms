import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'

export const NetPrice = memo(({
  country
}) => {
  return (
    <Input
      onChange={() => {}}
      id='asdasd'
      label='test'
      hideLabel
      type='number'
      prepend='GBP'
      tooltip='asdad'
      example='<p>To decide a final price for Dove gin we thought about:</p><ul><li>how much it cost to make one bottle of our gin</li><li>the average price for a bottle of gin in Australia</li></ul><p>This helped us decide where our product would sit in the market.</p><p>A bottle of our gin costs £15 to make, so to make a profit we had to charge over £15. Looking at Australian prices we decided on £25 a bottle in line with the market prices there. This gives us a profit margin of £10 on every unit sold.</p>'
      description={`<h2 class="h-xs p-t-0 p-b-0">Your net price per unit in the ${country}</h2><p class="m-t-xs">Deciding on what price your product will be sold for in retailers can be a difficult decision.</p><p class="m-b-0">You want to make sure you sell your product for more than it cost to make it, this way you make a profit on every unit sold.</p>`}
    />
  )
})

NetPrice.propTypes = {
  country: PropTypes.string.isRequired
}
