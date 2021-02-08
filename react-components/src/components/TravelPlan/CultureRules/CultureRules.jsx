import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import Services from '@src/Services'
import { Tooltip } from '@components/tooltip/Tooltip'
import { FormElements } from '@src/components/FormElements'

export const CultureRules = (params) => {
  const { tooltip } = params
  return (
    <>
      <h2 className="h-m m-b-xs">Culture and rules in your target market</h2>
      <p>
        Every country will have different rules you have stick by whilst you are
        visiting.
      </p>
      <p>
        Record any rules or information you need to conduct business in your
        target market.
      </p>
      <Tooltip {...tooltip} className="inline-block" />
      <FormElements {...params} />
    </>
  )
}
