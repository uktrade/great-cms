import React from 'react'

import { FormElements } from '@src/components/FormElements'

export const AdaptToTargetMarketForm = (params) => {
  return (
    <div className="form-table bg-blue-deep-10 radius p-h-s p-v-xs">
      <div className="target-market-form">
        <FormElements {...params} />
      </div>
    </div>
  )
}
