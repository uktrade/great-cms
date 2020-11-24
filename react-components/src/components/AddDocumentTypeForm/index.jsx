/* eslint-disable react/button-has-type */
/* eslint-disable jsx-a11y/label-has-associated-control */
/* eslint-disable import/prefer-default-export */
import React, { useEffect, useState } from 'react'
import { Input } from '@src/components/Form/Input'
import { TextArea } from '@src/components/Form/TextArea'
import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'

// List the user defined other documents
const DocumentList = (props) => {
  const { documents, deleteDocument, updateDocument } = props
  return (
    <div className="target-market-documents-form">
      {documents.length > 0
        ? documents.map((document) => (
            <form
              key={document.name}
              style={{
                position: 'relative',
              }}
              onBlur={() => {
                updateDocument(document)
              }}
            >
              <button
                className="button button--delete button--small button--only-icon button--tertiary"
                onClick={(e) => deleteDocument(e, document.name)}
              >
                <i className="fas fa-trash-alt" />
              </button>
              <Input
                label="Document name"
                id={document.name}
                placeholder="Add document name here"
                value={document.label}
                onChange={() => null}
              />
              <TextArea
                onChange={() => null}
                key={document.name}
                label="Notes"
                id={document.name}
                value={document.description}
                placeholder="Add notes"
                currency={document.currency}
                tag={Number.isInteger(document.placeholder) ? 'number' : 'text'}
              />
            </form>
          ))
        : ''}
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
  const documentsData = [
    { name: 'export_certificate_1', label: 'Export certificate', description: 'Some description data here' },
    {
      name: 'food_standards_certificate_1',
      label: 'Food standards certificate',
      description: 'Some description data here',
    },
    { name: 'duty_calculation_1', label: 'Duty calculation', description: 'Some description data here' },
  ]

  const [documents, setDocuments] = useState(documentsData)

  const addDocument = (document) => {
    const { name } = document
    document.label = name
    document.name = name.replace(/\s/g, '_').toLowerCase()
    setDocuments([...documents, document])
  }

  const deleteDocument = (event, name) => {
    event.preventDefault()
    setDocuments(documents.filter((document) => document.name !== name))
  }

  const updateDocument = (document) => {
    console.log(document)
    // const { name, value } = event.target
    setDocuments(
      documents.map((item) => {
        return item.name === document.name ? document : item
      })
    )
  }

  return (
    <>
      <FormWithInputWithExample {...props} />
      <DocumentList documents={documents} deleteDocument={deleteDocument} updateDocument={updateDocument} />
      <AddNewDocument addDocument={addDocument} />
    </>
  )
}
