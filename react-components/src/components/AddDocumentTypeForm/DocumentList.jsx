import React from 'react'
import { Input } from '@src/components/Form/Input'
import { TextArea } from '@src/components/Form/TextArea'

export const DocumentList = (props) => {
  const { documents, deleteDocument, updateDocument } = props
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
                  updateDocument(doc.pk, {
                    document_name: e[doc.pk],
                  })
                }
              />
              <TextArea
                onChange={(e) =>
                  updateDocument(doc.pk, {
                    note: e[doc.pk],
                  })
                }
                key={doc.name}
                label="Notes"
                id={doc.pk}
                value={doc.note}
                placeholder="Add notes"
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
