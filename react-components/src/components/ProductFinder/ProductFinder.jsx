import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import { capitalize } from '@src/Helpers'
import Spinner from '../Spinner/Spinner'
import Confirmation from './MessageConfirmation'
import Interaction from './Interaction'
import ValueInteraction from './ValueInteraction'
import ExpandCollapse from './ExpandCollapse'


const formatPath = (pathstr) => {
  return pathstr.split('//').map((part, index) => {
    return `${index > 0 ? ' > ' : ''}${capitalize(part)}`
  })
}

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
    openProductFinder(!selectedProduct)
  }

  const closeModal = () => {
    setIsOpen(false)
    setSearchResults({})

  }

  const closeConfirmation = () => {
    setProductConfirmationRequired(false)
    openProductFinder(true)
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
        window.location.reload()
      })
      .catch(() => {
        // TODO: add an error dialogue here
      })
  }

  const openProductFinder = (open) => {
    setIsOpen(open)
    if (open) {
      addTagging({
        'event': 'addProductPageview',
        'virtualPageURL': '/add-product-modal/search_entry',
        'virtualPageTitle': 'Add Product Modal - Search Entry'
      })
    }
  }

  const addTagging = (tag) => {
    if (window.dataLayer) {
      window.dataLayer.push(tag);
    }
  }

  const modalAfterOpen = () => {
    setIsScrolled(false)
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
    setSearchEnabled(!!evt.target.value)
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

  const onChangeClick = (evt) => {
    // TODO: Change handling will be added after UR, but we want the button to be available 
    evt.preventDefault()
  }

  const Section = (title, sectionDetails) => {
    if (!sectionDetails || sectionDetails.length === 0 || !sectionDetails.map) return ''
    return (
      <section className="p-h-l">
        <h3 className="h-m p-v-xs">{title}</h3>
          {(sectionDetails || []).map((value) => {
            return value.type === 'SELECTION' ? 
              (<Interaction txId={searchResults.txId} key={value.id} attribute={value} isItemChoice={sectionDetails.isItemChoice} processResponse={processResponse}/>) : 
              (<ValueInteraction txId={searchResults.txId} key={value.id} attribute={value} processResponse={processResponse} mixedContentError={searchResults.mixedContentError}/>)
          })}
      </section>
    )
  }

  const readOnlyContent = (sectionDetails) => {
    const content = (sectionDetails || []).map((interaction) => {
      return (
        <div className="grid m-v-xs" key={interaction.id}>
          <div className="c-fullwidth">
            <span className="bold p-t-0">{capitalize(interaction.label)}</span>
            <p className="m-v-xxs">
              {capitalize(interaction.selectedString)} 
              {interaction.selectedString === 'other' ? ` than ${interaction.unselectedString}` : ''}
              {' '}<button type="button" className="link link--underline body-m" onClick={onChangeClick}>Change</button>
            </p>
           </div>
        </div>)
    })
    return content
  }

  const sectionAssumptions = (sectionDetails) => {
    return sectionDetails && sectionDetails.length && (
      <section className="p-h-l">
        <h3 className="h-s p-0">Assumptions</h3>
        <p className="m-v-xxs">We&apos;ve answered some questions for you. View and change these if they&apos;re wrong.</p>
        <ExpandCollapse buttonLabel={ `View assumptions (${sectionDetails.length})`} expandedButtonLabel="Hide assumptions">{readOnlyContent(sectionDetails)}</ExpandCollapse> 
      </section>
    ) || ''
  }

  const sectionProductDetails = (sectionDetails) => {
    return sectionDetails && sectionDetails.length && (
      <div>
        <section className="p-h-l">
          <h3 className="h-s p-0">Product details</h3>
          <p className="m-v-xxs">Things you&apos;ve told us about your product.</p>
          {readOnlyContent(sectionDetails)}
        </section>
        <hr className="hr bg-black-10 m-h-l" />
      </div>
    ) || ''
  }

  const sectionFound = (_searchResults) => {
    return (
      <section className="m-h-l">
        <div className="h-m p-b-s">Match for &quot;{_searchResults.currentItemName}&quot;</div>
        <div className="box box--no-pointer">
          <h3 className="h-xs p-v-0">{capitalize(_searchResults.currentItemName)}</h3>
          <div className="body-m">HS Code: {_searchResults.hsCode}</div>
          <p>{formatPath(_searchResults.currentSIP)}</p>
          <button className="button button--primary" type="button" onClick={saveProduct}>
            Select this product
          </button>
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

    const sections = itemChoice ?
      // If the item is ambiguous - supress other sections
      <div>
        {!searchResults.hsCode && Section('Please choose your item', itemChoice)}
      </div> :
      <div>
        {!searchResults.hsCode && Section(`Tell us more about "${searchResults.currentItemName}"`, questions)}
        {(known || questions) ? (<hr className="hr hr--dark bg-deep-red-100 m-h-l"/>) : ''}
        {sectionProductDetails(known)} 
        {sectionAssumptions(assumptions)}
      </div>


    return (
      <div>
        {spinner}
        <div className="scroll-inner p-b-m">
          {searchResults.txId && !questions && !searchResults.hsCode && (
            <div className="grid p-t-l">
              <p className="h-s center">No results found</p>
            </div>
          )}
          {searchResults.hsCode && sectionFound(searchResults)}
          {sections}
        </div>
      </div>
    )
  }

  const buttonClass = `tag ${!selectedProduct ? 'tag--tertiary' : ''} tag--icon`
  const scrollerClass = `scroll-area ${isScrolled ? 'scroll-shadow' : ''}`
  const headerHeight = '210px'

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
        shouldCloseOnOverlayClick={false}
      >
        <form className="product-finder text-blue-deep-80">
          <div style={{height:headerHeight}}>        
            <button id="dialog-close" type="button" aria-label="Close" className="pull-right m-r-0 dialog-close" onClick={closeModal}/>
            <h3 className="h-l p-t-0 p-b-xxs">Search by name</h3>
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
              <button className="search-button button button--small button--only-icon m-f-xs" disabled={!searchEnabled} type="button" onClick={search}>
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
        messageTitle="Changing product?"
        messageBody="if you've created an export plan, make sure you update it to reflect your new product. you can change product at any time."
        messageButtonText="Got it"
      />
    </span>
  )
}

ProductFinder.propTypes = {
  text: PropTypes.string,
}

ProductFinder.defaultProps = {
  text: '',
}

export default function createProductFinder({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  const text = params.element.getAttribute('data-text')
  ReactDOM.render(<ProductFinder text={text}/>, params.element)
}
