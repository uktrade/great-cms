/* eslint-disable import/prefer-default-export */
import React from 'react'

import { FormElements } from '@src/components/FormElements'

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
        tooltip: `<p>
          Labelling is used to inform the consumer about the product you are selling to them.
          Labelling will need to be changed to fit into the market you are selling to. For example some pictures and colours may not be appropriate for certain markets.
          You will have to research what the requirements are so your products have the correct labels for your target market.
        </p>`,
      },
      {
        name: 'packaging',
        label: 'Packaging',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: `<p>
          Packaging provides protection for your product and prepares your product to be safely stored and transported.
          The information you need to include on your packaging will change depending on the market.
          You will have to research packaging requirements for your target market to avoid your products becoming damaged, lost or rejected.
        </p>`,
      },
      {
        name: 'size',
        label: 'Size',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: `<p>
          Standard product sizes vary by country depending on factors like buying habits in each market. 
          You will have to research the size of products sold in this market so you meet customer needs for your target market.
        </p>`,
      },
      {
        name: 'standards',
        label: 'Product changes to comply with standards',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: `<p>
          Your product will have to comply with local standards, if it does not comply it will not be allowed to be sold.
          You will have to research standards relevant to your product to make sure they are compliant.
        </p>`,
      },
      {
        name: 'translations',
        label: 'Translations',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: `<p>
          Some markets will require you by law to label and package your products in the local language. 
          You will have to research the language requirements for your market so your product labels comply with language requirements.
        </p>`,
      },
      {
        name: 'other_changes',
        label: 'Other changes',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: null,
      },
    ],
    formData: { ...formData },
  }
  return (
    <div className="form-table bg-blue-deep-10 radius p-h-s p-v-xs">
      <div className="objective-fields">
        <div className="target-market-form">
          <FormElements {...data} />
        </div>
      </div>
    </div>
  )
}
