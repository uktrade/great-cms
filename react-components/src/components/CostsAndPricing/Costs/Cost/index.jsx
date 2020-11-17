import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Input } from '@src/components/Form/Input'
import EducationalMomentTooltip from '@src/components/EducationalMomentTooltip'

export const Cost = memo(({
  label,
  id,
  currency,
  heading,
  description
}) => {
  return (
    <>
      <tr>
        <td>
          <Input
            label={label}
            id={id}
          />
        </td>
        <td>
          <span className='body-l'>{currency}</span>
        </td>
        <td>
          <EducationalMomentTooltip heading={heading} description={description} id='name' type='LEFT' />
        </td>
      </tr>
    </>
  )
})

Cost.propTypes = {
  label: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  heading: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
}
