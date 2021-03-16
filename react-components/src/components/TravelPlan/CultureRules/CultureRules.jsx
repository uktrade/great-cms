import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import { Tooltip } from '@components/tooltip/Tooltip'
import { FormElements } from '@src/components/FormElements'

export const CultureRules = memo((params) => {
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
})

CultureRules.propTypes = {
  params: PropTypes.shape({
    companyexportplan: PropTypes.string.isRequired,
    field: PropTypes.string.isRequired,
    formData: PropTypes.objectOf(
      PropTypes.shape({
        cultural_information: PropTypes.string,
        travel_information: PropTypes.string,
      })
    ),
    formFields: PropTypes.arrayOf(
      PropTypes.shape({
        description: PropTypes.string,
        field_type: PropTypes.string,
        label: PropTypes.string,
        name: PropTypes.string,
        placeholder: PropTypes.string,
      })
    ).isRequired,
    tooltip: PropTypes.objectOf(
      PropTypes.shape({
        content: PropTypes.string,
      }).isRequired
    ),
  }),
}
