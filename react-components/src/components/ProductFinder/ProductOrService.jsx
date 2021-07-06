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
          <div className="grid m-v-xs segmentation-modal m-f-0">
            <RadioButtons
              name={'p_or_s'}
              choices={[
                { label: 'I want to export <b>Products</b>', value: 'p' },
                { label: 'I want to sell a <b>Service</b> overseas', value: 's' },
              ]}
              valueChange={setStore}
            />
          </div>
          <button
            className="button button--primary save-product"
            type="button"
            onClick={() => selectProductOrService(store)}
          >
            Next
          </button>
        </section>
      </div>
    </>
  )
}
