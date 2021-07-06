import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import { Select } from '@src/components/Form/Select'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { dateFormat } from '@src/Helpers'
import Services from '@src/Services'
import actions from '@src/actions'
import StartEndPage from './StartEndPage'
import KeyValueList from './KeyValueList'

const checkChars = /^[a-zA-Z0-9\s~!@#£$%°^&*()-_+={}[\]|\\/:;"'<>,.?]*$/
const testInput = /[a-zA-Z]+/

export default function ServiceSearch(props) {
  const { complete } = props
  const debounceRate = 250
  const minChars = 3

  const [currentPage, setCurrentPage] = useState('company')
  const [resultList, setResultList] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [sicCodes, setSicCodes] = useState({})
  const [chosenSic, setChosenSic] = useState()

  useEffect(() => {
    Services.choicesApi({ choice: 'SIC_SECTOR_MAPPING' }).then((results) => {
      setSicCodes(
        (results || []).reduce((out, row) => {
          out[row['SIC code']] = row
          return out
        }, {})
      )
    })
  }, [])


  const selectValueChange = (newValue) => {
    const newCode = newValue.service_search
    const mapping = sicCodes[newCode]
    setInputValue(mapping['SIC description'])
    setChosenSic(newCode)
  }

  const mapResultsToChoices = () => {
    // Build structure to show in drop-down
    if (!resultList || !resultList.length) return ''
    return resultList.map((item) => ({
      label: (
        <>
          {sicCodes[item.code]['SIC description']}
          {<div className="body-m text-blue-deep-60">
            SIC code: {item.code}
          </div>}
        </>
      ),
      value: item.code,
    }))
  }

  const searchService = (term) => {
      const terms = (term || '').toLowerCase().trim().split(' ').filter((str) => str.length > minChars )
      const resultList = Object.keys(sicCodes).reduce((out,code) => {
        const description = sicCodes[code]['SIC description'].toLowerCase()
        const score = terms.filter((t) => description.indexOf(t) >= 0).length
        if(score) out.push({code,score})
        return out
      }, [])
      resultList.sort((a,b) => a.score === b.score ? (a.code > b.code ? 1 : -1) : (a.score > b.score ? -1 : 1))
      console.log(resultList)
      setResultList(resultList)
    }


  const inputChange = (evt) => {
    // on a change of the text input on search page
    const newInputValue = evt.target.value
    setInputValue(newInputValue)
    searchService(newInputValue)
  }

  const formatDate = (date) => {
    return date ? dateFormat(date) : ''
  }

  return(
      <>
        <div className="autocomplete">
          <p>
            Type in the name of the service you offer
          </p>
          <div className="m-v-s">
            <Select
              autoComplete
              label=""
              id="service_name"
              update={selectValueChange}
              name="service_search"
              options={mapResultsToChoices(resultList) || []}
              hideLabel
              placeholder="Service name"
              inputChange={inputChange}
              inputValue={inputValue}
              className="m-b-xs"
            />
          </div>
        </div>
        <button
          className="m-t-s button button--primary save-product"
          type="button"
          disabled={!chosenSic}
          onClick={() => complete(chosenSic)}
        >
          Next
        </button>
      </>
    )
}
