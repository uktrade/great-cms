import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import { Select } from '@src/components/Form/Select'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { dateFormat } from '@src/Helpers'
import Services from '@src/Services'
import KeyValueList from './KeyValueList'

const checkChars = /^[a-zA-Z0-9\s~!@#£$%°^&*()-_+={}[\]|\\/:;"'<>,.?]*$/
const testInput = /[a-zA-Z]+/

export default function ServiceFinder(props) {
  const { selectProductOrService } = props
  const debounceRate = 250
  const minChars = 3

  const [currentPage, setCurrentPage] = useState('company')
  const [resultList, setResultList] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [sicCodes, setSicCodes] = useState({})
  const [chosenSic, setChosenSic] = useState()

  const [company, setCompany] = useState(null)

  const validateKeys = (inputString) => {
    return checkChars.test(inputString)
  }

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

  //**********************    CH search
  const selectValueChange = (newValue) => {
    // choose company from search selector
    const companyNumber = Object.values(newValue)[0]
    const selectedCompany =
      resultList && resultList.find((co) => co.company_number === companyNumber)
    Services.companiesHouseApi({
      service: 'profile',
      company_number: companyNumber,
    }).then((results) => {
      setCompany({ ...selectedCompany, sic_codes: (results || {}).sic_codes })
    })
    setInputValue(selectedCompany.company_name)
  }

  const mapResultsToChoices = () => {
    // Build structure to show in drop-down
    if (!resultList)
      return [
        {
          value: 'error',
          label:
            'No results. Try a different search term. Click the link above if you cannot find your business.',
          isError: true,
        },
      ]

    return resultList.map((item) => ({
      label: (
        <>
          {item.company_name}
          <div className="body-m text-blue-deep-60">
            Company number: {item.company_number}
          </div>
        </>
      ),
      value: item.company_number,
    }))
  }

  const searchCompany = useDebounce((term) => {
    if (!term || term.length < minChars) {
      setResultList([])
    } else {
      Services.companiesHouseApi({ service: 'search', term }).then(
        (results) => {
          setResultList(
            results.items && results.items.length ? results.items : null
          )
        }
      )
    }
  }, debounceRate)
  const inputChange = (evt) => {
    // on a change of the text input on search page
    const newInputValue = evt.target.value
    setInputValue(newInputValue)
    searchCompany(newInputValue)
  }

  //***********  End ch search

  const formatDate = (date) => {
    return date ? dateFormat(date) : ''
  }

  const companyFieldMapping = [
    { key: 'company_name', name: 'Company name' },
    { key: 'company_number', name: 'Company number' },
    { key: 'date_of_creation', name: 'Incorporated on', format: formatDate },
    { key: 'address_snippet', name: 'Address' },
  ]

  const sicSectorDisplayMapping = [
    { key: 'SIC code', name: 'SIC code' },
    { key: 'SIC description', name: 'Description' },
    { key: 'DIT full sector name', name: 'DIT sector' },
  ]

  let pageContent
  if (currentPage == 'company') { pageContent = <>
        <div className="autocomplete">
          <p>
            If your company is registered with Companies House, we can find the
            services you offer

          <button
            className="link m-t-xxs"
            type="button"
            onClick={() => setMode(modes.manual)}
          >
            <span className="link link--underline body-l">
              I cannot find my business name OR my business is not registered
              with Companies House.
            </span>
          </button>
            </p>
          <div m-v-s>
            <Select
              autoComplete
              label=""
              id="company_name"
              update={selectValueChange}
              name="company_search"
              options={mapResultsToChoices(resultList) || []}
              hideLabel
              placeholder="Company name"
              inputChange={inputChange}
              inputValue={inputValue}
              className="m-b-xs"
            />
          </div>
        </div>
        {company ? (<KeyValueList item={company} mapping={companyFieldMapping}/>
        ) : (
          ''
        )}
        <button
          className="m-t-s button button--primary save-product"
          type="button"
          disabled={!company}
          onClick={() => setCurrentPage('sic_codes')}
        >
          Next
        </button>
      </>}

if (currentPage == 'sic_codes') { pageContent = <>
        <h3 className="h-s">SIC code list</h3>
        <ul>
          {(company.sic_codes || []).map((code) => (
            <li key={code} className="multiple-choice">
            <input
          id={code}
          type="radio"
          className="radio"
          name="sic-code-choice"
          value={code}
            onChange={setChosenSic}
            onClick={setChosenSic}
        />
            <label htmlFor={code}>
            <KeyValueList item={sicCodes[code]} mapping={sicSectorDisplayMapping}/>
            </label>
            </li>
          ))}
          <li key="no_code" className="multiple-choice">
            <input
            id="no_code"
            type="radio"
            className="radio"
            name="sic-code-choice"
            value="no_code"
            onChange={setChosenSic}
            onClick={setChosenSic}
          />
          <label htmlFor="no_code">
          <div className="g-panel p-t-0 p-b-xxs">
          <p>None of these</p>
          </div>
          </label>
          </li>
        </ul>
        <button
          className="m-t-s button button--primary"
          type="button"
          disabled={!chosenSic}
          onClick={() => {setCurrentPage(chosenSic == 'no_code' ? 'search_code' : 'selected_code') }}
        >
          Next
        </button>
      </>
  }
  if (currentPage == 'search_code') { pageContent = <>
    Search for a code
  </>
}
  if (currentPage == 'selected_code') { pageContent = <>
    Code Selected
  </>
}

  return (
    <>
      <section className="m-h-s m-v-s">
        <h2 className="h-m p-b-s">Add a service</h2>
        <div className="m-v-xs">{pageContent}</div>
      </section>
    </>
  )
}
