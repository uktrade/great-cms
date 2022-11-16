import React from 'react'
import { AddDocumentTypeForm } from '@src/components/AddDocumentTypeForm'
import { Learning } from '@src/components/Learning/Learning'

export const DocumentsForTargetMarketForm = (params) => {
  return (
    <>
      <Learning lesson={params.lesson} />
      <div className="form-table export-plan-form p-h-s p-v-xs">
        <div className="target-market-form">
          <AddDocumentTypeForm {...params} />
        </div>
      </div>
    </>
  )
}
