/* eslint-disable import/prefer-default-export */
import React from 'react'

import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'

export const AdaptToTargetMarketForm = (params) => {
  const data = {
    field: 'adaptation_target_market',
    formData: {
      size: 'uuu',
      labelling: 'sdsd',
      packaging: 'dddd',
      standards: 'yyy',
      translations: 'd',
    },
    formFields: [
      {
        name: 'labelling',
        label: 'Labelling',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip:
          'Labelling is used to inform the consumer about the product you are selling to them. Labelling will need to be changed to fit into the market you are selling to. For example some pictures and colours may not be appropriate for certain markets. You will have to research what the requirements are so your products have the correct labels for your target market.',
        example: '',
        description: '',
        currency: '',
        choices: '',
      },
      {
        name: 'packaging',
        label: 'Packaging',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip:
          'Packaging provides protection for your product and prepares your product to be safely stored and transported. The information you need to include on your packaging will change depending on the market.You will have to research packaging requirements for your target market to avoid your products becoming damaged, lost or rejected.',
        example: '',
        description: '',
        currency: '',
        choices: '',
      },
      {
        name: 'size',
        label: 'Size',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip:
          'Standard product sizes vary by country depending on factors like buying habits in each market. Consumers who buy less may want larger products to last them longer between shopping trips. You will have to research the size of products sold in this market so you meet customer needs for your target market.',
        example: '',
        description: '',
        currency: '',
        choices: '',
      },
      {
        name: 'standards',
        label: 'Product changes to comply with standards',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip:
          'Your product will have to comply with local standards, if it does not comply it will not be allowed to be sold. For example you may have to change the voltage of electrical products in order to comply with safety regulations in that market. You will have to research standards relevant to your product to make sure they are compliant.',
        example: '',
        description: '',
        currency: '',
        choices: '',
      },
      {
        name: 'translations',
        label: 'Translations',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: 'Translations',
        example: '',
        description: '',
        currency: '',
        choices: '',
      },
      {
        name: 'other_changes',
        label: 'Other changes',
        field_type: 'Textarea',
        placeholder: 'Describe alterations',
        tooltip: 'Other changes',
        example: '',
        description: '',
        currency: '',
        choices: '',
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
