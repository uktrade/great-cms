/* eslint-disable react/button-has-type */
/* eslint-disable jsx-a11y/label-has-associated-control */
/* eslint-disable import/prefer-default-export */
import React, { useState } from 'react'
import { Input } from '@src/components/Form/Input'
import { TextArea } from '@src/components/Form/TextArea'
import { FormElements } from '@src/components/FormElements'

// List the user defined other documents
const DocumentList = (props) => {
  const { documents, deleteDocument, updateDocument } = props

  return (
    <div className="target-market-documents-form">
      {documents.length > 0
        ? documents.map((document) => (
            <form key={document.name} className="user-form-group">
              <Input
                label="Document name"
                id={document.document_name}
                placeholder="Add document name here"
                value={document.label}
                onChange={(e) =>
                  updateDocument(document.label, {
                    label: e[document.document_name],
                  })
                }
              />
              <TextArea
                onChange={(e) =>
                  updateDocument(document.label, {
                    description: e[document.document_notes],
                  })
                }
                key={document.name}
                label="Notes"
                id={document.document_notes}
                value={document.description}
                placeholder="Add notes"
                currency={document.currency}
                tag={Number.isInteger(document.placeholder) ? 'number' : 'text'}
              />
              <div className="form-delete m-b-xs">
                <button
                  title="Click to delete this document and its notes."
                  className="button button--delete button--small button--only-icon button--tertiary"
                  onClick={(e) => deleteDocument(document.name, e)}
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
        if (!document.name || !document.description) return

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
  const initialData = [
    {
      name: 'export_certificate_1',
      label: 'Export certificate',
      description: 'Some description data here',
      document_name: 'export_certificate_1_name',
      document_notes: 'export_certificate_1_notes',
    },
    {
      name: 'food_standards_certificate_1',
      label: 'Food standards certificate',
      description: 'Some description data here',
      document_name: 'food_standards_certificate_1_name',
      document_notes: 'food_standards_certificate_1_notes',
    },
    {
      name: 'duty_calculation_1',
      label: 'Duty calculation',
      description: 'Some description data here',
      document_name: 'duty_calculation_1_name',
      document_notes: 'duty_calculation_1_notes',
    },
  ]

  const [documents, setDocuments] = useState(initialData)

  const addDocument = (document) => {
    const { name } = document
    document.label = name
    document.name = name.replace(/\s/g, '_').toLowerCase()
    document.document_name = document.name + '_name'
    document.document_notes = document.name + '_notes'
    setDocuments([...documents, document])
  }

  const deleteDocument = (name, event) => {
    event.preventDefault()
    setDocuments(documents.filter((document) => document.name !== name))
  }

  const updateDocument = (label, property) => {
    // debugger
    // console.log(label, property)
    setDocuments(
      documents.map((x) => (x.label === label ? { ...x, ...property } : x))
    )
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
