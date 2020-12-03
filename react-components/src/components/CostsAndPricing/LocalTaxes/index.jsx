import React from 'react'

import { Input } from '@src/components/Form/Input'

export const LocalTaxes = () => {
  return (
    <Input
      onChange={() => {}}
      id='asdasd'
      label='test'
      hideLabel
      type='number'
      prepend='GBP'
      example='<p>Value added tax (VAT) standard rate: 21%</p><p>Value added tax (VAT) reduced rate: 6%</p>'
      description='<h2 class="h-xs p-t-0 p-b-0">Local taxes and charges in the Netherlands</h2><p class="m-t-xs">You will need to pay taxes on your exports and these rates will change depending on which market you are selling in.</p><p>The following box displays the rate of tax you need to pay based on your chosen market.</p>'
      tooltip='asd asda sd'
    />
  )
}

