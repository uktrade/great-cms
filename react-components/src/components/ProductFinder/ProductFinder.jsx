import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { getModalIsOpen, getProductsExpertise } from '@src/reducers'
import Services from '@src/Services'

const customStyles = {
  content: {
    top: '0',
    right: '0',
    bottom: '0',
    left: 'auto',
    minWidth: '600px',
    width: '800px',
    padding: '0',
    border: 'none',
  },
  overlay: {
    background: 'rgb(45 45 45 / 45%)',
    zIndex: '3',
  },
}

function ValueChooser(attribute, handleChange) {
  const changeValue = (element) => {
    console.log(combinationValue) // TODO WIP
  }
  let startCombinationValue = {}
  let profile = (attribute.attrs || []).map((option, index) => {
    startCombinationValue[option.id] = option.value
    return (
      <label key={option.id} htmlFor={option.id} className="p-f-m m-b-xxs grid">
        <div className="c-1-4">
          <input
            type="number"
            className="form-control"
            id={option.id}
            name={attribute.id}
            defaultValue={option.value}
            data-label={option.name}
            onChange={changeValue}
          />
        </div>
        <div className="c-3-4">{option.name}</div>
      </label>
    )
  })

  return (
    <div>
      {profile}
      <button class="button button--primary" onClick={handleChange}>
        Send
      </button>
    </div>
  )
}

export function ProductFinder(props) {
  var searchInput
  const [modalIsOpen, setIsOpen] = React.useState(false)
  const [selectedProduct, setSelectedProduct] = React.useState(props.text)
  const [searchResults, setSearchResults] = React.useState([])

  const openModal = () => {
    setIsOpen(true)
  }

  const closeModal = () => {
    setIsOpen(false)
    setSearchResults({})
  }

  const saveProduct = () => {
    setSelectedProduct(searchResults.hsCode)
    Services.updateExportPlan({
      commodity_name: searchResults.currentItemName,
      export_commodity_codes: [searchResults.hsCode],
    })
      .then((result) => {
        closeModal()
      })
      .catch((result) => {
        // TODO: add an error dialogue here
      })
  }

  const modalAfterOpen = () => {
    searchInput.focus()
  }

  const inputKeypress = (evt) => {
    if (evt.key == 'Enter') {
      evt.preventDefault()
      search()
    }
  }

  const search = () => {
    let query = searchInput.value
    Services.lookupProduct({ q: query })
      .then((result) => {
        console.log('Initial search result', result); // TODO: Needed during development 
        setSearchResults(result && result.data);
      })
      .catch(() => {
        setSearchResults(result || {})
      })
  }

  const RadioButtons = (attribute, handleChange) => {
    let buttons = (attribute.attrs || []).map((option, index) => {
      return (
        <label key={option.id} htmlFor={option.id} className="multiple-choice p-f-m m-b-xxs">
          <input
            type="radio"
            className="radio"
            id={option.id}
            name={attribute.id}
            value={option.id}
            data-label={option.name}
            defaultChecked={option.value == 'true'}
          />
          {option.name}
          <label htmlFor={option.id}></label>
        </label>
      )
    })
    return <div onChange={handleChange}>{buttons}</div>
  }

  const Attribute = (attribute) => {
    const handleChange = (event) => {
      Services.lookupProductRefine({
        txId: searchResults.txId,
        attributeId: attribute.id,
        valueId: event.target.value,
        valueString: event.target.getAttribute('data-label'),
      })
        .then((result) => {
          console.log('***   refine result', result); // TODO: Needed during developmen
          if (result && result.data && result.data.txId) {
            setSearchResults(result && result.data)
          } else {
            setSearchResults(searchResults) // force re-render to reset any changed selectors
          }
        })
        .catch((error) => {
          // TODO: add an error dialogue here
          setSearchResults({})
        })
    }
    let body = { SELECTION: RadioButtons, VALUED: ValueChooser }[attribute.type](attribute, handleChange)

    return (
      <div className="grid m-v-s" key={attribute.id}>
        <div className="c-1-4 h-s p-t-0 capitalize">{attribute.label.replace(/_/g, ' ')}</div>
        <div className="c-3-4">{body}</div>
      </div>
    )
  }

  const Section = (title, sectionDetails) => {
    if (!sectionDetails || sectionDetails.length == 0 || !sectionDetails.map) return null
    return (
      <section className="summary">
        <h3 className="h-m p-0">{title}</h3>
        <div className="">
          {(sectionDetails || []).map((value, index) => {
            return Attribute(value)
          })}
        </div>
      </section>
    )
  }

  return (
    <span>
      <button className="button button--primary button--round-corner" onClick={openModal}>
        {selectedProduct || 'add product'}
      </button>
      <ReactModal isOpen={modalIsOpen} onRequestClose={closeModal} style={customStyles} onAfterOpen={modalAfterOpen}>
        <form className="product-finder">
          <div className="search-header bg-blue-deep-80 text-white p-s">
            <button className="pull-right m-r-0" onClick={closeModal}>
              <span className="fa fa-window-close"></span>
            </button>
            <h3 className="h-m text-white p-t-0">Search by name</h3>
            <div>Find the product you want to export</div>
            <input
              className="form-control c-2-3"
              type="text"
              ref={(_searchInput) => (searchInput = _searchInput)}
              onKeyPress={inputKeypress}
              defaultValue=""
            />
            <button className="button button--tertiary m-f-xxs" type="button" onClick={search}>
              Search
            </button>
          </div>
          <div className="classification-result">
            {searchResults.hsCode && (
              <section className="found-section grid bg-black-10">
                <div className="c-1-3">
                  <span className="h-m">You've found your product!</span>
                </div>
                <div className="c-1-3">
                  <div className="h-s p-t-0">{searchResults.currentItemName}</div>
                  hs code: <span className="bold">{searchResults.hsCode}</span>
                </div>
                <div className="c-1-3">
                  <button className="button button--primary" type="button" onClick={saveProduct}>
                    Select this product
                  </button>
                </div>
              </section>
            )}

            {false && searchResults.productDescription && (
              <section className="summary table">
                <div className="table-row">
                  <div className="table-cell">Here's what we know about your</div>
                  <div className="table-cell bold">{searchResults.productDescription}</div>
                </div>
              </section>
            )}
            {Section(
              `Tell us more about your '${searchResults.currentItemName}'`,
              searchResults.currentQuestionInteraction && [searchResults.currentQuestionInteraction]
            )}
            {false &&
              Section(
                'Please choose your item',
                searchResults.currentItemInteraction && [searchResults.currentItemInteraction]
              )}
            {Section(`Your item's characteristics`, searchResults.knownInteractions)}
            {Section("We've assumed:", searchResults.assumedInteractions)}
          </div>
        </form>
      </ReactModal>
    </span>
  )
}

export default function ({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  let text = params.element.innerText
  ReactDOM.render(<ProductFinder text={text}></ProductFinder>, params.element)
}
