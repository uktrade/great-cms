/* eslint-disable import/prefer-default-export */
import React from 'react'

import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'

export const AdaptToTargetMarketForm = (params) => {
  const { formData } = params
  const data = {
    field: 'adaptation_target_market',
    formFields: [
      {
        name: 'labelling',
        label: 'Labelling',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: 'Labelling tooltip',
      },
      {
        name: 'packaging',
        label: 'Packaging',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: 'Packaging tooltip',
      },
      {
        name: 'size',
        label: 'Size',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: 'Size tooltip',
      },
      {
        name: 'standards',
        label: 'Product changes to comply with standards',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: 'Product changes to comply with standards tooltip',
      },
      {
        name: 'translations',
        label: 'Translations',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: 'Translations tooltip',
      },
      {
        name: 'other_changes',
        label: 'Other changes',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: 'Other changes tooltip',
      },
    ],
    formData: { ...formData },
  }
  return (
    <div className="form-table bg-blue-deep-10 radius p-h-s p-v-xs">
      <div className="objective-fields">
        <div className="target-market-form">
          <FormWithInputWithExample {...data} />
        </div>
      </div>
    </div>
  )
}
