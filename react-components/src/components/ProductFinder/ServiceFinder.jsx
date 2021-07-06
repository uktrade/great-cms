import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import { Select } from '@src/components/Form/Select'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { dateFormat } from '@src/Helpers'
import Services from '@src/Services'
import actions from '@src/actions'
import StartEndPage from './StartEndPage'
import ServiceSearch from './ServiceSearch'
import KeyValueList from './KeyValueList'

const checkChars = /^[a-zA-Z0-9\s~!@#£$%°^&*()-_+={}[\]|\\/:;"'<>,.?]*$/
const testInput = /[a-zA-Z]+/

export default function ServiceFinder(props) {
  const { closeModal } = props
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

  const saveProduct = (commodityCode, commodityName) => {
    Services.store.dispatch(
      actions.setProduct({
        commodity_name: commodityName,
        commodity_code: commodityCode,
      })
    )
    closeModal()
  }

  let pageContent
  if (currentPage == 'company') {
    pageContent = (
      <>
        <div className="autocomplete">
          <p>
            If your company is registered with Companies House, we can find the
            services you offer
            <button
              className="link m-t-xxs"
              type="button"
              onClick={() => setCurrentPage('search_code')}
            >
              <span className="link link--underline body-l">
                I cannot find my business name OR my business is not registered
                with Companies House.
              </span>
            </button>
          </p>
          <div className="m-v-s">
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
        {company ? (
          <KeyValueList item={company} mapping={companyFieldMapping} />
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
      </>
    )
  }

  if (currentPage == 'sic_codes') {
    pageContent = (
      <>
        <h3 className="h-s">Choose one of your company's SIC codes</h3>
        <div className="grid segmentation-modal">
          <ul>
            {(company.sic_codes || []).map((code) => (
              <li key={code} className="multiple-choice">
                <input
                  id={code}
                  type="radio"
                  className="radio"
                  name="sic-code-choice"
                  value={code}
                  onChange={() => setChosenSic(code)}
                  onClick={() => setChosenSic(code)}
                />
                <label htmlFor={code}>
                   {sicCodes[code] && sicCodes[code]['SIC description']}
                   &nbsp;<b>({sicCodes[code] && sicCodes[code]['SIC code']})</b>
                  {/*<KeyValueList
                    item={sicCodes[code]}
                    mapping={sicSectorDisplayMapping}
                  />*/}
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
                onChange={() => setChosenSic('no_code')}
                onClick={() => setChosenSic('no_code')}
              />
              <label htmlFor="no_code">
                Search for another service
              </label>
            </li>
          </ul>
        </div>
        <button
          className="m-t-s button button--primary"
          type="button"
          disabled={!chosenSic}
          onClick={() => {
            if (chosenSic == 'no_code') {
              setCurrentPage('search_code')
            } else {
              setCurrentPage('selected_code')
              //saveProduct(chosenSic, sicCodes[chosenSic]['SIC description'])
            }
          }}
        >
          Next
        </button>
      </>
    )
  }
  if (currentPage == 'search_code') {
    pageContent = <ServiceSearch complete={(sicCode) => {
      setChosenSic(sicCode)
      setCurrentPage('selected_code')
    }}/>
  }
  if (currentPage == 'selected_code') {
    pageContent = <StartEndPage
          commodityCode={chosenSic}
          defaultCommodityName={sicCodes[chosenSic]['SIC description']}
          saveProduct={saveProduct}
          searchCompletedMode={true}
        />
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
