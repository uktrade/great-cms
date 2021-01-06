/* eslint-disable react/button-has-type */
/* eslint-disable jsx-a11y/label-has-associated-control */
/* eslint-disable import/prefer-default-export */
import React, { useState } from 'react'
import { Input } from '@src/components/Form/Input'
import { TextArea } from '@src/components/Form/TextArea'
import { FormElements } from '@src/components/FormElements'
import Services from '@src/Services'
import { useDebounce } from '@src/components/hooks/useDebounce'

// List the user defined other documents
const DocumentList = (props) => {
  const { documents, deleteDocument, updateDocument } = props
  debugger
  return (
    <div className="target-market-documents-form">
      {documents.length > 0
        ? documents.map((doc) => (
            <form key={doc.pk} className="user-form-group">
              <Input
                label="Document name"
                id={doc.pk}
                placeholder="Add document name here"
                value={doc.document_name}
                onChange={(e) =>
                  updateDocument(doc.label, {
                    label: e[doc.document_name],
                  })
                }
              />
              <TextArea
                onChange={(e) =>
                  updateDocument(doc.label, {
                    description: e[doc.note],
                  })
                }
                key={doc.name}
                label="Notes"
                id={doc.pk}
                value={doc.note}
                placeholder="Add notes"
                currency={doc.currency}
                tag={Number.isInteger(doc.placeholder) ? 'number' : 'text'}
              />
              <div className="form-delete m-b-xs">
                <button
                  title="Click to delete this document and its notes."
                  className="button button--delete button--small button--only-icon button--tertiary"
                  onClick={(e) => deleteDocument(doc.pk, e)}
                >
                  <i className="fas fa-trash-alt" />
                </button>
              </div>
            </form>
          ))
        : null}
    </div>
  )
}

// Add a new document to the list
const AddNewDocument = (props) => {
  const { addDocument } = props
  const initialFormState = { name: '', label: '', description: '' }
  const [document, setDocument] = useState(initialFormState)

  const handleInputChange = (event) => {
    const { name, value } = event.target

    setDocument({ ...document, [name]: value })
  }
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        // if (!document.name || !document.description) return

        addDocument(document)
        setDocument(initialFormState)
      }}
    >
      <div className="form-group">
        <label className="form-label" htmlFor="name">
          Document name
        </label>
        <input
          id="name"
          type="text"
          name="name"
          value={document.name}
          placeholder="Add document name here"
          onChange={handleInputChange}
          className="form-control"
        />
        <label className="form-label" htmlFor="description">
          Notes
        </label>
        <textarea
          type="text"
          id="description"
          name="description"
          value={document.description}
          placeholder="Add notes"
          onChange={handleInputChange}
          className="form-control"
        />
        <button className="button button--small button--secondary button--icon m-t-s">
          <i className="fas fa-plus-circle" />
          <span>Add another document</span>
        </button>
      </div>
    </form>
  )
}

// The parent component
export const AddDocumentTypeForm = (props) => {
  const initialData = props.formData

  const [documents, setDocuments] = useState(initialData)
  console.log(initialData)
  // const addDocumentOld = (document) => {
  //   const { name } = document
  //   document.label = name
  //   document.name = name.replace(/\s/g, '_').toLowerCase()
  //   document.document_name = document.name + '_name'
  //   document.note = document.name + '_note'
  //   setDocuments([...documents, document])
  // }

  // const deleteDocumentOld = (name, event) => {
  //   event.preventDefault()
  //   setDocuments(documents.filter((document) => document.name !== name))
  // }

  // const updateDocumentOld = (label, property) => {
  //   // debugger
  //   // console.log(label, property)
  //   setDocuments(
  //     documents.map((x) => (x.label === label ? { ...x, ...property } : x))
  //   )
  // }

  const addDocument = (document) => {
    const { name, description } = document

    document.document_name = name
    document.note = description

    Services.createAdaptTarketMarketDocumentList({
      ...document,
      companyexportplan: props.companyexportplan,
    })
      .then((data) => setDocuments([...documents, data]))
      // .then(() => {
      //   const newElement = document.getElementById(
      //     `Route to market ${routes.length + 1}`
      //   ).parentNode
      //   newElement.scrollIntoView()
      // })
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

  const updateDocument = (label, property) => {
    Services.updateAdaptTarketMarketDocumentList({ ...label, ...property })
      .then(() => {
        setDocuments(
          documents.map((x) => (x.label === label ? { ...x, ...property } : x))
        )
      })
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
      <AddNewDocument addDocument={addDocument} />
    </>
  )
}
