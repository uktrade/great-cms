/* eslint-disable prefer-destructuring */
import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import Spinner from '../Spinner/Spinner'
import Confirmation from './MessageConfirmation'

function ProductFinder(props) {
  const { text } = props;
  let searchInput
  const [modalIsOpen, setIsOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState(text)
  const [searchResults, setSearchResults] = useState([])
  const [isLoading, setLoading] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [searchEnabled, setSearchEnabled] = useState(false)
  const [productConfirmationRequired, setProductConfirmationRequired] = useState(false)

  const openModal = () => {
    setProductConfirmationRequired(!!selectedProduct)
    setIsOpen(!selectedProduct)
  }

  const closeModal = () => {
    setIsOpen(false)
    setSearchResults({})
  }

  const closeConfirmation = () => {
    setProductConfirmationRequired(false)
    setIsOpen(true)
  }

  const saveProduct = () => {
    setSelectedProduct(searchResults.currentItemName)
    Services.updateExportPlan({
        export_commodity_codes: [{
          commodity_name: searchResults.currentItemName,
          commodity_code: searchResults.hsCode
        }]
      })
      .then(() => {
        closeModal()
      })
      .catch(() => {
        // TODO: add an error dialogue here
      })
  }

  const modalAfterOpen = () => {
    searchInput.focus()
  }

  const processResponse = (request) => {
    setLoading(true)
    request
      .then((result) => {
        setLoading(false)
        /* eslint-disable no-console */
        console.log('Search result', result) // TODO: Needed during development
        /* eslint-enable no-console */
        if (result && result.data && result.data.txId) {
          setSearchResults(result.data)
        } else {
          setSearchResults(searchResults) // force re-render to reset any changed selectors
        }
      })
      .catch(() => {
        setLoading(false)
        setSearchResults({})
      })
  }

  const search = () => {
    const query = searchInput.value
    if (query) {
      processResponse(Services.lookupProduct({ q: query }))
    }
  }

  const inputKeypress = (evt) => {
    if (evt.key === 'Enter') {
      evt.preventDefault()
      search()
    }
  }

  const inputChange = (evt) => {
    const value = evt.target.value
    setSearchEnabled(!!value)
  }

  const clearSearchInput = (evt) => {
    const input = evt.target.parentElement.querySelector('input')
    input.value = ''
    input.focus()
    setSearchEnabled(false)
  }

  const onScroll = (evt) => {
    setIsScrolled(evt.target.scrollTop > 0)
  }


  const RadioButtons = (attribute, handleChange, setValue = true) => {
    const buttons = (attribute.attrs || []).map((option) => {
      return (
        <label key={option.id} htmlFor={option.id} className="multiple-choice p-f-m m-b-xxs">
          <input
            type="radio"
            className="radio"
            id={option.id}
            name={attribute.id}
            value={option.id}
            data-label={option.name}
            defaultChecked={setValue && option.value === 'true'}
            aria-label={option.name}
          />
          {option.name}
          {/* eslint-disable jsx-a11y/label-has-associated-control */}
          <label htmlFor={option.id}/>
          {/* eslint-enable jsx-a11y/label-has-associated-control */}
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
            valueString: event.target.getAttribute('data-label')
          })
        )
      }
    }

    const body = { SELECTION: RadioButtons, VALUED: RadioButtons } [attribute.type](
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
    if (!sectionDetails || sectionDetails.length === 0 || !sectionDetails.map) return null
    return (
      <section className="summary">
        <h3 className="h-s p-0">{title}</h3>
        <div className="">
          {(sectionDetails || []).map((value) => {
            return Attribute(value, sectionDetails)
          })}
        </div>
      </section>
    )
  }

  const buildMap = (block) => {
    // build an interaction block, removing any duplicates from previous
    const newBlock = []
    if (block && block.length) {
      for (let index = 0; index < block.length; index += 1) {
        const interaction = block[index]
        if (interaction && interaction.id) {
          newBlock.push(interaction)
        }
      }
    }
    return newBlock.length ? newBlock : null
  }

  const resultsDisplay = (results) => {
    // Build maps of interactions as we don't want any duplicates
    const questions = buildMap([results.currentQuestionInteraction])
    const assumptions = buildMap(results.assumedInteractions)
    const known = buildMap(results.knownInteractions)
    const itemChoice = buildMap([results.currentItemInteraction]);
    (itemChoice || {}).isItemChoice = true
    const spinner = isLoading ? (
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
                <span className="h-s">You&apos;ve found your product!</span>
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
                <div className="table-cell">Here&apos;s what we know about your</div>
                <div className="table-cell bold capitalize">{searchResults.productDescription}</div>
              </div>
            </section>
          )}
          {Section('Please choose your item', itemChoice)}
          {!itemChoice && Section(`Tell us more about your '${searchResults.currentItemName}'`, questions)}
          {!itemChoice && Section('Your item&apos;s characteristics', known)}
          {!itemChoice && Section('We\'ve assumed:', assumptions)}
        </div>
      </div>
    )
  }

  const buttonClass = `tag ${!selectedProduct ? 'tag--tertiary' : ''} tag--icon`
  const scrollerClass = `scroll-area ${isScrolled ? 'scrolled' : ''}`
  const headerHeight = '190px'

  return (
    <span>
      <button type="button" className={buttonClass} onClick={openModal}>
        {selectedProduct || 'add product'}
        <i className={`fa ${selectedProduct ? 'fa-edit' : 'fa-plus'}`}/>
      </button>
      <ReactModal 
        isOpen={modalIsOpen} 
        onRequestClose={closeModal} 
        className="modal max-modal p-v-s p-h-l"
        overlayClassName="modal-overlay center"
        onAfterOpen={modalAfterOpen}
      >
        <form className="product-finder">
          <div className="modal-header" style={{height:headerHeight}}>        
            <button id="dialog-close" type="button" aria-label="Save" className="pull-right m-r-0 dialog-close" onClick={closeModal}/>
            <h3 className="h-m p-t-0">Search by name</h3>
            <div>Find the product you want to export</div>
            <div className="flex-centre m-t-xs search-input">
              <div className="flex-centre">
                <input
                  className="form-control"
                  type="text"
                  ref={(_searchInput) => {searchInput = _searchInput}}
                  onKeyPress={inputKeypress}
                  onChange={inputChange}
                  defaultValue=""
                />
                <button type="button" aria-label="Clear" className="fa fa-times clear" onClick={clearSearchInput}/>
                </div>
              <button className="button button--small button--only-icon m-f-xs" disabled={!searchEnabled} type="button" onClick={search}>
                <i className="fa fa-arrow-right"/>
              </button>
            </div>
          </div>
          <div className={scrollerClass} style={{marginTop:headerHeight}} onScroll={onScroll}>
            {resultsDisplay(searchResults)}
          </div>
        </form>
      </ReactModal>
      <Confirmation
        buttonClass={buttonClass}
        productConfirmation={productConfirmationRequired}
        handleButtonClick={closeConfirmation}
        messsageTitle="Changing product?"
        messageBody="if you've created an export plan, make sure you update it to reflect your new product. you can change product at any time."
        messageButtonText="Got it"
      />
    </span>
  )
}

ProductFinder.propTypes = {
  text: PropTypes.string.isRequired,
}

export default function createProductFinder({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  const text = params.element.getAttribute('data-text')
  ReactDOM.render(<ProductFinder text={text}/>, params.element)
}
