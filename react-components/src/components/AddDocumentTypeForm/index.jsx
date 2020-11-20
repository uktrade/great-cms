/* eslint-disable import/prefer-default-export */
import React from 'react'
import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'

export const AddDocumentTypeForm = (params) => {
  return (
    <>
      <FormWithInputWithExample {...params} />
      <p>Docs component here</p>
    </>
  )
}
