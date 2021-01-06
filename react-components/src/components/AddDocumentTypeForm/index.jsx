import React, { useState } from 'react'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { FormElements } from '@src/components/FormElements'
import { DocumentList } from './DocumentList'

export const AddDocumentTypeForm = (props) => {
  const [documents, setDocuments] = useState(props.formData)

  const addDocument = () => {
    document.document_name = ''
    document.note = ''

    Services.createAdaptTarketMarketDocumentList({
      ...document,
      companyexportplan: props.companyexportplan,
    })
      .then((data) => setDocuments([...documents, data]))
      .catch(() => {})
  }

  const deleteDocument = (id, event) => {
    event.preventDefault()

    Services.deleteAdaptTarketMarketDocumentList(id)
      .then(() => {
        setDocuments(documents.filter((document) => document.pk !== id))
      })
      .catch(() => {})
  }

  const debounceUpdate = useDebounce(updateApi)

  const updateDocument = (id, property) => {
    const field = documents.find((x) => x.pk === id)
    setDocuments(
      documents.map((x) => (x.pk === id ? { ...x, ...property } : x))
    )
    updateApi(field, property)
  }

  const updateApi = (field, property) => {
    Services.updateAdaptTarketMarketDocumentList({ ...field, ...property })
      .then(() => {})
      .catch(() => {})
  }

  return (
    <>
      <FormElements {...props} />
      <DocumentList
        documents={documents}
        deleteDocument={deleteDocument}
        updateDocument={updateDocument}
      />
      <button
        className="button button--small button--secondary button--inherit button--icon m-t-s m-b-s"
        type="button"
        onClick={addDocument}
      >
        <i className="fas fa-plus-circle" />
        <span>Add another document</span>
      </button>
    </>
  )
}
