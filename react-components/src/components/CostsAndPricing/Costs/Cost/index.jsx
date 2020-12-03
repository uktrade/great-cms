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
    <tr>
      <td>
        <label className='form-label p-b-xs' htmlFor={id}>{label}</label>
        <EducationalMomentTooltip heading={heading} description={description} id='name' type='LEFT' />
      </td>
      <td>
        <Input
          label={label}
          id={id}
          hideLabel
          type='number'
          prepend={currency}
        />
      </td>
    </tr>
  )
})

Cost.propTypes = {
  label: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  currency: PropTypes.string.isRequired,
  heading: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
}
