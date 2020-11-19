import React from 'react'

import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'

export const DocumentsForTargetMarketForm = (params) => {
  const data = {
    field: 'documents_for_target_market',
    formData: {
      certOrigin: 'Some note text added',
      certInsurance: '',
      commercialInvoice: '',
      customsDeclaration: '',
    },
    formFields: [
      {
        name: 'certOrigin',
        label: 'Certificate of origin',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: 'Certificate of origin',
      },
      {
        name: 'certInsurance',
        label: 'Insurance certificate',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: 'Insurance certificate',
      },
      {
        name: 'commercialInvoice',
        label: 'Commercial invoice',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: 'Commercial invoice',
      },
      {
        name: 'customsDeclaration',
        label: 'UK customs declaration',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: 'UK customs declaration',
      },
    ],
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
