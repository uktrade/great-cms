import React, { useState } from 'react'

import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { FormElements } from '@src/components/FormElements'
import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'
import { objectHasValue } from '@src/Helpers'
import { DocumentList } from './DocumentList'

export const AddDocumentTypeForm = (props) => {
  const [documents, setDocuments] = useState(props.formDataUserDocs)

  const { companyexportplan, pk, ...lastField } = documents.length
    ? documents[documents.length - 1]
    : {}

  const addDocument = () => {
    const document = {}
    document.document_name = ''
    document.note = ''

    Services.createAdaptTarketMarketDocumentList({
      ...document,
      companyexportplan: props.companyexportplan,
    })
      .then((data) => setDocuments([...documents, data]))
      .catch(() => {})
  }

  const deleteDocument = (id) => {
    Services.deleteAdaptTarketMarketDocumentList(id)
      .then(() => {
        setDocuments(documents.filter((document) => document.pk !== id))
      })
      .catch(() => {})
  }

  const updateApi = (field, property) => {
    Services.updateAdaptTarketMarketDocumentList({ ...field, ...property })
      .then(() => {})
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(updateApi)

  const updateDocument = (id, property) => {
    const field = documents.find((x) => x.pk === id)
    setDocuments(
      documents.map((x) => (x.pk === id ? { ...x, ...property } : x))
    )
    debounceUpdate(field, property)
  }

  return (
    <>
      <FormElements {...props} />
      <DocumentList
        documents={documents}
        deleteDocument={deleteDocument}
        updateDocument={updateDocument}
      />
      <AddButton
        isDisabled={documents.length ? !objectHasValue(lastField) : false}
        add={addDocument}
        btnClass="button--small button--secondary button--inherit  m-t-s m-b-s"
        cta="Add another document"
      />
    </>
  )
}
