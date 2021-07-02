import React from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'

export default function KeyValueList(props) {
  const { item, mapping } = props
  return (
    <>
      <div className="g-panel p-t-0 p-b-xxs">
        {mapping.map((field) => {
          return (
            <div className="m-v-xxs" key={field.key}>
              <dt className="body-m-b">{field.name}</dt>
              <dt className="body-m">
                {(field.format
                  ? field.format(item[field.key])
                  : item[field.key]) || ''}
              </dt>
            </div>
          )
        })}
      </div>
    </>
  )
}
