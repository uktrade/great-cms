import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import { capitalize } from '@src/Helpers'
import Spinner from '../Spinner/Spinner'
import Interaction from './Interaction'
import ValueInteraction from './ValueInteraction'
import ExpandCollapse from './ExpandCollapse'
import SearchInput from './SearchInput'
import { analytics } from '../../Helpers'


const formatPath = (pathstr) => {
  return pathstr.split('//').map((part, index) => {
    return `${index > 0 ? ' > ' : ''}${capitalize(part)}`
  })
}

export default function ProductFinderModal(props) {
  const { modalIsOpen, setIsOpen, setSelectedProduct } = props;

  let scrollOuter

  const [searchResults, setSearchResults] = useState()
  const [isLoading, setLoading] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showingInteraction, setShowingInteraction] = useState()

  useEffect(() => {
    if (modalIsOpen) {
      analytics({
        'event': 'addProductPageview',
        'virtualPageUrl': '/add-product-modal/search_entry',
        'virtualPageTitle': 'Add Product Modal - Search Entry',
        productKeyword: null,
        productCode: null
      })
    }
  }, [modalIsOpen])

  const closeModal = () => {
    setIsOpen(false)
    setSearchResults()
  }

  const modalAfterOpen = () => {
    setIsScrolled({})
    setSearchTerm('')
  }

  const setScrollShadow = () => {
    if (scrollOuter) {
      const bottomOverflow = scrollOuter.scrollHeight - (scrollOuter.scrollTop + scrollOuter.clientHeight)
      setIsScrolled({ top: scrollOuter.scrollTop > 0, bottom: bottomOverflow > 0 })
    }
  }

  const onScroll = (evt) => {
    scrollOuter = evt.target
    setScrollShadow()
  }

  const resetScroll = () => {
    if (scrollOuter) {
      scrollOuter.scrollTop = 0;
      setScrollShadow();
    }
  }

  const saveProduct = () => {
    const productName = capitalize(searchResults.currentItemName)
    const searchQuery = capitalize(searchResults.productDescription)
    setSelectedProduct({
      name: productName,
      code: searchResults.hsCode
    })
    analytics({
      event: 'addProductSuccess',
      productKeyword: searchQuery,
      productCode: searchResults.hsCode
    })

    Services.updateExportPlan({
        export_commodity_codes: [{
          commodity_name: productName,
          commodity_code: searchResults.hsCode
        }]
      })
      .then(() => {
        closeModal()
        window.location.reload()
      })
      .catch(() => {
        closeModal()
      })
  }

  const renderSearchResults = (newSearchResults) => {
    setLoading(false)
    setSearchResults(newSearchResults)
    resetScroll()
  }

  const responseAnalytics = (result) => {
    const searchQuery = capitalize(result.productDescription);
    if (result.hsCode) {
      // product found
      analytics({
        event: 'addProductPageview',
        virtualPageUrl: '/add-product-modal/product-found',
        virtualPageTitle: 'Add Product Modal - Product Found',
        productKeyword: searchQuery,
        productCode: result.hsCode
      })
    } else if (result.currentQuestionInteraction) {
      if (result.knownInteractions.length === 0) {
        // 'tell us more', first response
        analytics({
          event: 'addProductPageview',
          virtualPageUrl: '/add-product-modal/tell-us-more',
          virtualPageTitle: 'Add Product Modal - Tell Us More',
          productKeyword: searchQuery
        })
      }
    } else {
      // product not found
      analytics({
        event: 'addProductPageview',
        virtualPageUrl: '/add-product-modal/no-results',
        virtualPageTitle: 'Add Product Modal - No Results',
        productKeyword: searchQuery
      })
    }
  }

  const processResponse = (request) => {
    setLoading(true)
    request
      .then((result) => {
        setShowingInteraction()
        if (result && result.data && result.data.txId) {
          responseAnalytics(result.data)
          renderSearchResults(result.data)
        } else {
          renderSearchResults(searchResults) // force re-render to reset any changed selectors
        }
      })
      .catch(() => {
        renderSearchResults()
      })
  }

  const search = () => {
    const query = searchTerm
    if (query) {
      processResponse(Services.lookupProduct({ proddesc: query }))
    }
  }

  const onChangeClick = (interaction) => {
    setShowingInteraction(interaction)
  }

  const backToSearch = () => {
    renderSearchResults()
  }

  const Section = (title, sectionDetails) => {
    if (!sectionDetails || sectionDetails.length === 0 || !sectionDetails.map) return ''
    return (
      <section className="p-h-l">
        <h3 className="h-m p-v-xs">{title}</h3>
          {(sectionDetails || []).map((value) => {
            return value.type === 'SELECTION' ? 
              (<Interaction txId={searchResults.txId} proddesc={searchResults.proddesc} key={value.id} attribute={value} isItemChoice={sectionDetails.isItemChoice} processResponse={processResponse}/>) : 
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
              {interaction.selectedString === 'other' ? ` ${interaction.unselectedString}` : ''}
              {' '}<button type="button" className="change-known-button link link--underline body-m" onClick={() => onChangeClick(interaction)}>Change</button>
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
      <section className="m-h-l m-b-s">
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

  const sectionNoResults = (_searchResults) => {
    return (
      <section className="m-h-l">
        <div className="box box--no-pointer p-h-s p-t-s p-b-xs m-t-xs">
          <h3 className="h-m p-t-xxs">No results found for &lsquo;{_searchResults.productDescription}&rsquo;</h3>
          <h4 className="h-xs">Search tips</h4>
          <ul className="list-dot m-v-xxs p-f-xs">
            <li>Check for spelling mistakes</li>
            <li>Try a more generic search term for describing your product, like sofa instead of settee</li>
          </ul>
          <h4 className="h-xs">Example searches</h4>
          <ul className="list-dot m-v-xxs p-f-xs">
            <li>frozen atlantic salmon</li>
            <li>strawberries</li>
            <li>fresh cut snowdrop</li>
            <li>Woven mens blazer, 75% wool, 25% cotton</li>
          </ul>
        </div>
      </section>
    )
  }
  const sectionMultiItem = () => {
    return (
      <section className="m-h-l">
        <div className="box box--no-pointer p-h-s p-v-xs m-t-xs">
          <p>
            The item you are classifying is considered a complex item (or set) which normally requires each component to be classified separately. 
            Alternatively, you may request a binding classification ruling for your complex item (or set) from Customs in the country of import.
          </p>
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

  const spinner = isLoading ? (
    <div className="shim">
      <Spinner text="" />
    </div>
  ) : (
    ''
  )

  const resultsDisplay = (results) => {
    // Build maps of interactions as we don't want any duplicates

    let questions = buildMap([results.currentQuestionInteraction])
    if (showingInteraction) {
      questions = [showingInteraction]
    }
    const assumptions = buildMap(results.assumedInteractions)
    const known = buildMap(results.knownInteractions)
    let itemChoice = buildMap([results.currentItemInteraction]);
    (itemChoice || {}).isItemChoice = true

    // *********************   Kill item choice so we can just use question 
    itemChoice = null

    if (searchResults.multiItemError) {
      return sectionMultiItem(searchResults)
    }

    if (searchResults.txId && !questions && !searchResults.hsCode) {
      return sectionNoResults(searchResults)
    }

    const sections = itemChoice && !searchResults.hsCode ?
      // If the item is ambiguous - supress other sections
      <div>
        {Section('Please choose your item', itemChoice)}
      </div> :
      <div>
        {!showingInteraction && searchResults.hsCode && sectionFound(searchResults)}
        {(!searchResults.hsCode || showingInteraction) && Section(`Tell us more about "${searchResults.currentItemName}"`, questions)}
        {((known || questions) && !showingInteraction ) ? (<hr className="hr bg-red-deep-100 m-h-l"/>) : ''}
        {!showingInteraction && sectionProductDetails(known)} 
        {!showingInteraction && sectionAssumptions(assumptions)}
      </div>

    return sections
  }

  const searchBox = () => {
    return (
      <div className="p-h-l p-v-l">
        <h3 className="h-m p-t-0 p-b-xxs">Search by name</h3>
        <div>Find the product you want to export</div>
        <div className="flex-centre m-t-xs search-input">
            <SearchInput
              onChange={setSearchTerm}
              onKeyReturn={search}
              autoFocus
            />
          <button className="search-button button button--small button--only-icon m-f-xs" disabled={!searchTerm} type="button" onClick={search}>
            <i className="fa fa-arrow-right"/>
          </button>
        </div>
      </div>
    )
  }

  const scrollerClass = `scroll-area ${isScrolled && isScrolled.top ? 'scroll-shadow-top' : ''} ${isScrolled && isScrolled.bottom ? 'scroll-shadow-bottom' : ''}`
  const headerHeight = '0px'

  return (
    <span>
      <ReactModal 
        isOpen={modalIsOpen} 
        onRequestClose={closeModal} 
        className="modal max-modal p-v-s p-h-l"
        overlayClassName="modal-overlay center"
        onAfterOpen={modalAfterOpen}
        shouldCloseOnOverlayClick={false}
        style={{
          content:{
            width:'auto',
            left: '100px',
            right: '100px',
            overflow: 'hidden',
          }
        }}
      >
        <form className="product-finder text-blue-deep-80">
          <div style={{height:headerHeight}}>
            {/* nothing in the modal header for the time being */}
          </div>
          <div 
            className={scrollerClass} 
            style={{marginTop:headerHeight}} 
            onScroll={onScroll}
          >
            <button id="dialog-close" type="button" aria-label="Close" className="pull-right m-r-0 dialog-close" onClick={closeModal}/>
            {spinner}
            <div 
              className="scroll-inner p-b-m"
              ref={(_scrollInner) => {scrollOuter = _scrollInner || scrollOuter}}
            >
              {!searchResults ? searchBox() : (<button type="button" className="back-button m-f-l m-t-m" onClick={backToSearch} ><i className="fa fa-arrow-circle-left m-r-xs"/>Search again</button>)}
              {searchResults && resultsDisplay(searchResults)}
            </div>
          </div>
        </form>
      </ReactModal>
    </span>
  )
}

ProductFinderModal.propTypes = {
  modalIsOpen: PropTypes.bool.isRequired,
  setIsOpen: PropTypes.func.isRequired,
  setSelectedProduct: PropTypes.func.isRequired,
}
