/* eslint-disable import/prefer-default-export */
import React from 'react'

import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'

export const DocumentsForTargetMarketForm = (params) => {
  const { formData } = params
  const data = {
    field: 'adaptation_target_market',
    formFields: [
      {
        name: 'certificate_of_origin',
        label: 'Certificate of origin',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: 'Certificate of origin',
      },
      {
        name: 'insurance_certificate',
        label: 'Insurance certificate',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: 'Insurance certificate',
      },
      {
        name: 'commercial_invoice',
        label: 'Commercial invoice',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: 'Commercial invoice',
      },
      {
        name: 'uk_customs_declaration',
        label: 'UK customs declaration',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: 'UK customs declaration',
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
