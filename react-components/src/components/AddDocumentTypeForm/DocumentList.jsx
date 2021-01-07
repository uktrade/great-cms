import React from 'react'
import PropTypes from 'prop-types'
import { Input } from '@src/components/Form/Input'
import { TextArea } from '@src/components/Form/TextArea'

export const DocumentList = ({ documents, deleteDocument, updateDocument }) => {
  return (
    <div className="target-market-documents-form">
      {documents.length > 0
        ? documents.map((doc) => (
            <div key={doc.pk} className="user-form-group">
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
            </div>
          ))
        : null}
    </div>
  )
}

DocumentList.propTypes = {
  documents: PropTypes.array.isRequired,
  deleteDocument: PropTypes.func.isRequired,
  updateDocument: PropTypes.func.isRequired,
}
