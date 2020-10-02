import React, { useState } from 'react'
import ReactDOM from 'react-dom'

const CaseStudy = ({ content: { heading, company, body } }) => {
  const [isOpen, setIsOpen] = useState(false)
  return (
    <div className="m-b-l">
      {isOpen && (
        <button onClick={() => setIsOpen(false)}>
          <i class="fas fa-times"></i>
        </button>
      )}
      <h3 className="h-m m-b-xs">{heading}</h3>
      {isOpen && <p>{company}</p>}
      {!isOpen && (
        <button className="button button--tertiary" onClick={() => setIsOpen(true)}>
          Open case study
        </button>
      )}
      {isOpen && <div>{body}</div>}
    </div>
  )
}

function createCaseStudy({ element }) {
  ReactDOM.render(
    <CaseStudy
      content={{
        heading: 'France has proven a steady growth market for Joe and Steph',
        company: 'Joes Gourmet Foods Ltd',
        body:
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse sagittis ut est id finibus. Nulla ut porta erat. Nam id elementum tellus. In id orci dictum, lacinia velit sit amet, fringilla quam.'
      }}
    />,
    element
  )
}

export { CaseStudy, createCaseStudy }
