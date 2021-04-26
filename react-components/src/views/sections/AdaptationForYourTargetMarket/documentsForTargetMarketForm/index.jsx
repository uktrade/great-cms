import React from 'react'
import { AddDocumentTypeForm } from '@src/components/AddDocumentTypeForm'

export const DocumentsForTargetMarketForm = (params) => {
  return (
    <div className="form-table bg-blue-deep-10 radius p-h-s p-v-xs">
      <div className="target-market-form">
        <AddDocumentTypeForm {...params} />
      </div>
    </div>
  )
}
