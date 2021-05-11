import React, { useState } from 'react'

import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { FormElements } from '@src/components/FormElements'
import { AddButton } from '@src/components/ObjectivesList/AddButton/AddButton'
import { objectHasValue } from '@src/Helpers'
import { useUpdate } from '@src/components/hooks/useUpdate/useUpdate'
import ErrorList from '@src/components/ErrorList'
import { DocumentList } from './DocumentList'

export const AddDocumentTypeForm = (props) => {
  const [documents, setDocuments] = useState(props.formDataUserDocs)

  const { companyexportplan, pk, ...lastField } = documents.length
    ? documents[documents.length - 1]
    : {}

  const [update, create, deleteItem, message, errors] = useUpdate(
    'adapting-your-product'
  )

  const addDocument = () => {
    create({
      document_name: '',
      note: '',
      companyexportplan: props.companyexportplan,
      model_name: props.model_name,
    }).then((data) => setDocuments([...documents, data]))
  }

  const deleteDocument = (id) => {
    deleteItem({ pk: id, model_name: props.model_name }).then(() => {
      setDocuments(documents.filter((document) => document.pk !== id))
    })
  }

  const updateApi = (field, property) =>
    update({ ...field, ...property, model_name: props.model_name })

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
      <ErrorList errors={errors.__all__ || []} className="m-0" />
    </>
  )
}
