import React, { useState } from 'react'
import PropTypes from 'prop-types'
import ReactHtmlParser from 'react-html-parser'
import Services from '@src/Services'
import { dateFormat } from '@src/Helpers'
import { useDebounce } from '@src/components/hooks/useDebounce'
import { Select } from '@src/components/Form/Select'
import { Input } from '@src/components/Form/Input'
import Modal from './Modal'

export default function CompanyNameModal(props) {
  const {
    question,
    value,
    setValue,
    nextButtonClick,
    backButtonClick,
    closeClick,
    progressPercentage,
  } = props

  const modes = { review: 1, manual: 2, search: 3 }
  const debounceRate = 250
  const minChars = 3

  const [resultList, setResultList] = useState([])
  const [inputValue, setInputValue] = useState(
    (value && value.company_name) || ''
  )
  const [company, setCompany] = useState(value)
  const [mode, setMode] = useState(
    (value && (value.company_number ? modes.review : modes.manual)) ||
      modes.search
  )

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

  const inputChange = (evt) => {
    // on a change of the text input on search page
    const newInputValue = evt.target.value
    setInputValue(newInputValue)
    searchCompany(newInputValue)
  }

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

  const primaryButtonClick = () => {
    if (mode === modes.review || mode === modes.manual) {
      nextButtonClick()
    } else {
      setMode(modes.review)
      setValue(company)
    }
  }

  const goBack = () => {
    if (mode === modes.review) {
      setMode(modes.search)
    } else {
      backButtonClick()
    }
  }

  const manualInputChange = (newValue) => {
    // User typing company name manually. Update company and output value
    const companyName = Object.values(newValue)[0]
    setInputValue(Object.values(newValue)[0])
    setCompany((companyName || '').length > 2 ? newValue : null)
    setValue(newValue)
  }

  const formatDate = (date) => {
    return date ? dateFormat(date) : ''
  }

  const companyFieldMapping = [
    { key: 'company_name', name: 'Company name' },
    { key: 'company_number', name: 'Company number' },
    { key: 'date_of_creation', name: 'Incorporated on', format: formatDate },
    { key: 'address_snippet', name: 'Address' },
  ]

  const getContent = () => {
    if (mode === modes.search)
      return (
        <div className="autocomplete">
          <div>{ReactHtmlParser(question.choices.searchContent)}</div>
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
          <Select
            autoComplete
            label=""
            id="company_name"
            update={selectValueChange}
            name="company_search"
            options={mapResultsToChoices(resultList) || []}
            hideLabel
            placeholder={question.choices.placeholder}
            inputChange={inputChange}
            inputValue={inputValue}
          />
        </div>
      )
    if (mode === modes.manual)
      return (
        <>
          <div>{ReactHtmlParser(question.choices.manualContent)}</div>
          <button
            className="link m-t-xxs"
            type="button"
            onClick={() => setMode(modes.search)}
          >
            <span className="link link--underline body-l">
              My business is registered with Companies House.
            </span>
          </button>
          <Input
            label=""
            id="company_name"
            placeholder={question.choices.placeholder}
            value={inputValue}
            onChange={manualInputChange}
            hideLabel
          />
        </>
      )
    // Must be review
    return (
      <>
        <div>{ReactHtmlParser(question.choices.reviewContent)}</div>
        <div className="g-panel p-t-0 p-b-xxs">
          {companyFieldMapping.map((item) => {
            return (
              <div className="m-v-xxs" key={item.key}>
                <dt className="body-m-b">{item.name}</dt>
                <dt className="body-m">
                  {(item.format
                    ? item.format(company[item.key])
                    : company[item.key]) || ''}
                </dt>
              </div>
            )
          })}
        </div>
      </>
    )
  }

  return (
    <Modal
      className="segmentation-modal"
      title={question.title}
      body={
        <form className="text-blue-deep-80">
          <div className="c-fullwidth">{getContent()}</div>
        </form>
      }
      progressPercentage={progressPercentage}
      primaryButtonLabel="Next"
      primaryButtonClick={primaryButtonClick}
      primaryButtonDisable={!company}
      secondaryButtonLabel={mode === modes.review ? 'Search again' : 'Back'}
      secondaryButtonClick={goBack}
      closeClick={closeClick}
    />
  )
}

CompanyNameModal.propTypes = {
  question: PropTypes.shape({
    name: PropTypes.string,
    type: PropTypes.string,
    id: PropTypes.number,
    title: PropTypes.string,
    choices: PropTypes.oneOfType([
      PropTypes.shape({
        options: PropTypes.arrayOf(
          PropTypes.shape({
            value: PropTypes.string,
          })
        ),
        placeHolder: PropTypes.string,
      }),
      PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.string,
        })
      ),
    ]),
  }).isRequired,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.objectOf(
      PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.objectOf(PropTypes.string),
        PropTypes.arrayOf(PropTypes.string),
      ])
    ),
  ]).isRequired,
  setValue: PropTypes.func.isRequired,
  nextButtonClick: PropTypes.func.isRequired,
  backButtonClick: PropTypes.func.isRequired,
  closeClick: PropTypes.func.isRequired,
  progressPercentage: PropTypes.number.isRequired,
}
