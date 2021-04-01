import React from 'react'

import { FormElements } from '@src/components/FormElements'
import { Learning } from '@src/components/Learning/Learning'

export const AdaptToTargetMarketForm = (params) => {
  const { lesson } = params
  return (
    <>
      <h3 className="h-l">Changes to your product</h3>
      <p>
        Write down whether you need to make changes to any of the following and
        include relevant details.
      </p>
      <Learning lesson={lesson} />
      <br />
      <div className="form-table bg-blue-deep-10 radius p-h-s p-v-xs">
        <div className="target-market-form">
          <FormElements {...params} />
        </div>
      </div>
    </>
  )
}
