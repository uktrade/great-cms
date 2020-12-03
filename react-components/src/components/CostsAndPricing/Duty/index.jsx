import React from 'react'

import { Input } from '@src/components/Form/Input'

export const Duty = () => {
  return (
    <div>
      <Input
        onChange={() => {}}
        id="asdasd"
        label="test"
        hideLabel
        type="number"
        prepend="GBP"
        description='<h2 class="h-xs p-t-0 p-b-0">Duty per unit</h2><p class="m-t-xs m-b-0">The Withdrawal Agreement between the EU and the UK entered into force on 1 February 2020. The UK has entered a transition period until 31 December 2020. During the transition period, there will continue to be no duty charged on UK exports by EU member states.</p>'
        tooltip='asdasd asd '
      />
    </div>
  )
}

