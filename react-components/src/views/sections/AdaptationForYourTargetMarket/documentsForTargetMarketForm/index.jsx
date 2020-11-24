/* eslint-disable import/prefer-default-export */
import React from 'react'
import { AddDocumentTypeForm } from '@src/components/AddDocumentTypeForm'

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
        tooltip: `The certificate of origin is a document that declares which country a product comes from and where it is going. 
        It helps customs officials decide if a product can be imported or if it is subject to duties costs.`,
      },
      {
        name: 'insurance_certificate',
        label: 'Insurance certificate',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: `Export insurance insures an exporter against the risk of not being paid or not being able to recover costs of a contract.
        You will have to research exporter insurance to find out what insurance is best for you and your product.`,
      },
      {
        name: 'commercial_invoice',
        label: 'Commercial invoice',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: `A commercial invoice is a document that contains information about:

        The goods you are exporting, tariff codes, the value of your goods, the country of origin, incoterms and transaction numbers.
        
        It is one of the main documents used by customs officials to calculate duties and taxes and it also makes sure you get paid on time.`,
      },
      {
        name: 'uk_customs_declaration',
        label: 'UK customs declaration',
        field_type: 'Textarea',
        placeholder: 'Add note',
        tooltip: `An export declaration is a form submitted at the port when goods are leaving the country. The form has details about the goods and where they are heading.

        It is needed on all goods that are being exported outside the EU.`,
      },
    ],
    formData: { ...formData },
  }
  return (
    <div className="form-table bg-blue-deep-10 radius p-h-s p-v-xs">
      <div className="objective-fields">
        <div className="target-market-form">
          <AddDocumentTypeForm {...data} />
        </div>
      </div>
    </div>
  )
}
