import React, { useState } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import ClassificationTree from './ClassificationTree'
import SearchInput from './SearchInput'
import { analytics } from '../../Helpers'
import RadioButtons from '@src/components/Segmentation/RadioButtons'

const checkChars = /^[a-zA-Z0-9\s~!@#£$%°^&*()-_+={}[\]|\\/:;"'<>,.?]*$/
const testInput = /[a-zA-Z]+/

export default function ProductOrService(props) {
  const { selectProductOrService } = props

  const [store, setStore] = useState(null)

  const validateKeys = (inputString) => {
    return checkChars.test(inputString)
  }

  return (
    <>
          <div className="p-h-s p-t-l">
        <section className="m-b-s">
      <h2 className="h-m p-b-s">About your export</h2>
      <p>Do you intend to export a product or a service?</p>
      <div className="grid m-v-xs">
      <RadioButtons
        name={'p_or_s'}
        choices={[
          { label: 'Product', value: 'p' },
          { label: 'Service', value: 's' },
        ]}
        valueChange={setStore}
      />
      </div>
      <button className="button button--primary save-product" type="button" onClick={() => selectProductOrService(store)}>
        Next
      </button>
      </section>
      </div>
    </>
  )
}
