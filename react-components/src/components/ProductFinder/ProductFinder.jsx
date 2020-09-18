import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { getModalIsOpen, getProductsExpertise } from '@src/reducers'
import Services from '@src/Services'
import Spinner from '../Spinner/Spinner'

const customStyles = {
  content: {
    top: '0',
    right: '0',
    bottom: '0',
    left: 'auto',
    minWidth: '800px',
    padding: '0',
    border: 'none',
    overflow: 'none',
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
      <button className="button button--primary" onClick={handleChange}>
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
  const [isLoading, setLoading] = React.useState(false)
  const [isScrolled, setIsScrolled] = React.useState(false)

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

  const onScroll = (evt) => {
    setIsScrolled(evt.target.scrollTop > 0)
  }

  const processResponse = (request) => {
    setLoading(true)
    request
      .then((result) => {
        setLoading(false)
        console.log('Initial search result', result) // TODO: Needed during development
        if (result && result.data && result.data.txId) {
          setSearchResults(result.data)
        } else {
          setSearchResults(searchResults) // force re-render to reset any changed selectors
        }
      })
      .catch(() => {
        setLoading(false)
        setSearchResults(result || {})
      })
  }

  const search = () => {
    let query = searchInput.value
    processResponse(Services.lookupProduct({ q: query }))
  }

  const RadioButtons = (attribute, handleChange, setValue = true) => {
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
            defaultChecked={setValue && option.value == 'true'}
          />
          {option.name}
          <label htmlFor={option.id}></label>
        </label>
      )
    })
    return <div onChange={handleChange}>{buttons}</div>
  }

  const Attribute = (attribute, section) => {
    const handleChange = (event) => {
      if (section.isItemChoice) {
        processResponse(Services.lookupProduct({ q: event.target.getAttribute('data-label') }))
      } else {
        processResponse(
          Services.lookupProductRefine({
            txId: searchResults.txId,
            attributeId: attribute.id,
            valueId: event.target.value,
            valueString: event.target.getAttribute('data-label'),
          })
        )
      }
    }

    let body = { SELECTION: RadioButtons, VALUED: ValueChooser }[attribute.type](
      attribute,
      handleChange,
      !section.isItemChoice
    )

    return (
      <div className="grid m-v-s" key={attribute.id}>
        <div className="c-1-4 h-xs p-t-0 capitalize">{attribute.label.replace(/_/g, ' ')}</div>
        <div className="c-3-4">{body}</div>
      </div>
    )
  }

  const Section = (title, sectionDetails) => {
    if (!sectionDetails || sectionDetails.length == 0 || !sectionDetails.map) return null
    return (
      <section className="summary">
        <h3 className="h-s p-0">{title}</h3>
        <div className="">
          {(sectionDetails || []).map((value, index) => {
            return Attribute(value, sectionDetails)
          })}
        </div>
      </section>
    )
  }

  const buildMap = (block, map) => {
    // build an intetrraction block, removing any duplicates from previous
    let newBlock = []
    for (var index in block) {
      let interraction = block[index]
      if (interraction && interraction.id) {
        if (!map[interraction.id]) {
          map[interraction.id] = true
          newBlock.push(interraction)
        }
      }
    }
    return newBlock.length ? newBlock : null
  }

  const resultsDisplay = (searchResults) => {
    // Build maps of intteractions as we don't want any duplicates
    let iMap = {}
    let questions = buildMap([searchResults.currentQuestionInteraction], iMap)
    let assumptions = buildMap(searchResults.assumedInteractions, iMap)
    let known = buildMap(searchResults.knownInteractions, iMap)
    let itemChoice = buildMap([searchResults.currentItemInteraction], iMap)
    ;(itemChoice || {}).isItemChoice = true
    let spinner = isLoading ? (
      <div className="shim">
        <Spinner text="" />
      </div>
    ) : (
      ''
    )
    return (
      <div>
        {spinner}
        <div className="scroll-inner">
          {searchResults.txId && !questions && !searchResults.hsCode && (
            <div className="grid p-t-l">
              <p className="h-s center">No results found</p>
            </div>
          )}
          {searchResults.hsCode && (
            <section className="found-section grid bg-black-10">
              <div className="c-1-3">
                <span className="h-s">You've found your product!</span>
              </div>
              <div className="c-1-3">
                <div className="h-xs p-t-0 capitalize">{searchResults.currentItemName}</div>
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
                <div className="table-cell bold capitalize">{searchResults.productDescription}</div>
              </div>
            </section>
          )}
          {Section('Please choose your item', itemChoice)}
          {!itemChoice && Section(`Tell us more about your '${searchResults.currentItemName}'`, questions)}
          {!itemChoice && Section(`Your item's characteristics`, known)}
          {!itemChoice && Section("We've assumed:", assumptions)}
        </div>
      </div>
    )
  }

  let buttonClass = 'button ' + (selectedProduct ? 'button--secondary' : 'button--ghost-blue')+' button--round-corner button--chevron'
  let scrollerClass = 'scroll-area '+(isScrolled ? 'scrolled' : '')

  return (
    <span>
      <button className={buttonClass} onClick={openModal}>
        {selectedProduct || 'add product'}
      </button>
      <ReactModal isOpen={modalIsOpen} onRequestClose={closeModal} style={customStyles} onAfterOpen={modalAfterOpen}>
        <form className="product-finder">
          <div className="search-header bg-blue-deep-80 text-white p-s" style={{ height: '172px' }}>
            <button className="pull-right m-r-0 dialog-close" onClick={closeModal}></button>
            <h3 className="h-s text-white p-t-0">Search by name</h3>
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
          <div className={scrollerClass} style={{ marginTop: '172px' }} onScroll={onScroll}>
            {resultsDisplay(searchResults)}
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
  let text = params.element.getAttribute('data-text')
  ReactDOM.render(<ProductFinder text={text}></ProductFinder>, params.element)
}
