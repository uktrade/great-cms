import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import ReactHtmlParser from 'react-html-parser'
import Services from '@src/Services'
import actions from '@src/actions'
import { capitalize } from '@src/Helpers'
import Spinner from '../Spinner/Spinner'
import Interaction from './Interaction'
import ValueInteraction from './ValueInteraction'
import ExpandCollapse from './ExpandCollapse'
import SearchInput from './SearchInput'
import StartEndPage from './StartEndPage'
import { analytics } from '../../Helpers'


export default function ProductFinderModal(props) {
  const { modalIsOpen, setIsOpen, selectedProduct } = props

  let scrollOuter
  const [isSearching, setSearching] = useState(false)
  const [searchResults, setSearchResults] = useState()
  const [isLoading, setLoading] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showingInteraction, setShowingInteraction] = useState()

  useEffect(() => {
    if (modalIsOpen) {
      analytics({
        event: 'addProductPageview',
        virtualPageUrl: '/add-product-modal/search_entry',
        virtualPageTitle: 'Add Product Modal - Search Entry',
        productKeyword: null,
        productCode: null,
      })
    }
  }, [modalIsOpen])

  const closeModal = () => {
    setIsOpen(false)
    setSearching(false)
    setSearchResults()
  }

  const modalAfterOpen = () => {
    setIsScrolled({})
    setSearchTerm('')
  }

  const setScrollShadow = () => {
    if (scrollOuter) {
      const bottomOverflow =
        scrollOuter.scrollHeight -
        (scrollOuter.scrollTop + scrollOuter.clientHeight)
      setIsScrolled({
        top: scrollOuter.scrollTop > 0,
        bottom: bottomOverflow > 0,
      })
    }
  }

  const onScroll = (evt) => {
    scrollOuter = evt.target
    setScrollShadow()
  }

  const resetScroll = () => {
    if (scrollOuter) {
      scrollOuter.scrollTop = 0
      setScrollShadow()
    }
  }

  const saveProduct = (commodityCode, commodityName) => {
    Services.store.dispatch(
      actions.setProduct({
        commodity_name: commodityName,
        commodity_code: commodityCode,
      })
    )
    if (searchResults) {
      analytics({
        event: 'addProductSuccess',
        productKeyword: commodityName,
        productCode: commodityCode,
      })
    }
    closeModal()
  }

  const renderSearchResults = (newSearchResults) => {
    setLoading(false)
    setSearchResults(newSearchResults)
    resetScroll()
  }

  const responseAnalytics = (result) => {
    const searchQuery = capitalize(result.productDescription)
    if (result.hsCode) {
      // product found
      analytics({
        event: 'addProductPageview',
        virtualPageUrl: '/add-product-modal/product-found',
        virtualPageTitle: 'Add Product Modal - Product Found',
        productKeyword: searchQuery,
        productCode: result.hsCode,
      })
    } else if (result.currentQuestionInteraction) {
      if (result.knownInteractions.length === 0) {
        // 'tell us more', first response
        analytics({
          event: 'addProductPageview',
          virtualPageUrl: '/add-product-modal/tell-us-more',
          virtualPageTitle: 'Add Product Modal - Tell Us More',
          productKeyword: searchQuery,
        })
      }
    } else {
      // product not found
      analytics({
        event: 'addProductPageview',
        virtualPageUrl: '/add-product-modal/no-results',
        virtualPageTitle: 'Add Product Modal - No Results',
        productKeyword: searchQuery,
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
    setSearching(true)
    renderSearchResults()
    analytics({
      event: 'searchProductAgain',
    })
  }

  const Section = (title, sectionDetails) => {
    if (!sectionDetails || sectionDetails.length === 0 || !sectionDetails.map)
      return ''
    return (
      <section className="p-h-s">
        <h3 className="h-m p-v-xs">{title}</h3>
        {(sectionDetails || []).map((value) => {
          return value.type === 'SELECTION' ? (
            <Interaction
              txId={searchResults.txId}
              proddesc={searchResults.proddesc}
              key={value.id}
              attribute={value}
              isItemChoice={sectionDetails.isItemChoice}
              processResponse={processResponse}
            />
          ) : (
            <ValueInteraction
              txId={searchResults.txId}
              key={value.id}
              attribute={value}
              processResponse={processResponse}
              mixedContentError={searchResults.mixedContentError}
            />
          )
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
              {interaction.selectedString === 'other'
                ? ` ${interaction.unselectedString}`
                : ''}{' '}
              <button
                type="button"
                className="change-known-button link link--underline body-m"
                onClick={() => onChangeClick(interaction)}
              >
                Change
              </button>
            </p>
          </div>
        </div>
      )
    })
    return content
  }

  const sectionAssumptions = (sectionDetails) => {
    return (
      (sectionDetails && sectionDetails.length && (
        <section className="p-h-s">
          <h3 className="h-s p-0">Assumptions</h3>
          <p className="m-v-xxs">
            We&apos;ve answered some questions for you. View and change these if
            they&apos;re wrong.
          </p>
          <ExpandCollapse
            buttonLabel={`View assumptions (${sectionDetails.length})`}
            expandedButtonLabel="Hide assumptions"
          >
            {readOnlyContent(sectionDetails)}
          </ExpandCollapse>
        </section>
      )) ||
      ''
    )
  }

  const sectionProductDetails = (sectionDetails) => {
    return (
      (sectionDetails && sectionDetails.length && (
        <div>
          <section className="p-h-s">
            <h3 className="h-s p-0">Product details</h3>
            <p className="m-v-xxs">
              Things you&apos;ve told us about your product.
            </p>
            {readOnlyContent(sectionDetails)}
          </section>
          <hr className="hr bg-black-10 m-h-s" />
        </div>
      )) ||
      ''
    )
  }

  const sectionFound = (_searchResults) => {
    return (
      <section className="m-h-s m-b-s body-l">
        <div className="h-m p-b-s">Match found</div>
        <StartEndPage
          commodityCode={_searchResults.hsCode}
          defaultCommodityName={capitalize(_searchResults.currentItemName)}
          saveProduct={saveProduct}
        />
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
    let itemChoice = buildMap([results.currentItemInteraction])
    ;(itemChoice || {}).isItemChoice = true

    // *********************   Kill item choice so we can just use question
    itemChoice = null

    const sections =
      itemChoice && !searchResults.hsCode ? (
        // If the item is ambiguous - supress other sections
        <div>{Section('Please choose your item', itemChoice)}</div>
      ) : (
        <div>
          {!showingInteraction &&
            searchResults.hsCode &&
            sectionFound(searchResults)}
          {(!searchResults.hsCode || showingInteraction) &&
            Section(
              `Tell us more about "${searchResults.currentItemName}"`,
              questions
            )}
          {(known || questions) && !showingInteraction ? (
            <hr className="hr bg-red-deep-100 m-h-s" />
          ) : (
            ''
          )}
          {!showingInteraction && sectionProductDetails(known)}
          {!showingInteraction && sectionAssumptions(assumptions)}
        </div>
      )

    return sections
  }

  const searchBox = (error) => {
    return (
      <div className="p-h-s p-t-l">
        <h3 className="h-m p-t-0 p-b-xxs">Add product</h3>
        <div>
          Adding a product personalises lessons and other content for you.
        </div>
        {error && <div className="form-group-error p-v-xs m-v-xs">{error}</div>}
        <div className="flex-centre m-t-xs search-input">
          <SearchInput
            id="search-input"
            onChange={setSearchTerm}
            onKeyReturn={search}
            autoFocus
            iconClass="fa-search"
            placeholder="ie: fresh strawberries"
          />
          <button
            className="search-button button button--small button--only-icon m-f-xs"
            disabled={!searchTerm}
            type="button"
            onClick={search}
          >
            <i className="fa fa-arrow-right" />
          </button>
        </div>
        <div className="box box--no-pointer m-t-s">
          When you search for a product you may have to answer a few questions
          before you find a match.
        </div>
        <div className="box box--no-pointer m-t-s">
          <p className="m-t-0 m-b-xs">
            This is because we use HS (
            <span className="body-l-b">harmonised system</span>) codes to
            classify goods.
          </p>
          <p className="m-v-0">
            Think of it like the folder structure on a computer.
          </p>
        </div>
        <div className="box box--no-pointer m-t-s m-h-0 grid">
          <div className="c-1-2 p-h-0">
            <p className="m-t-0 m-b-xs">
              You might see your product as &quot;delicious green apples from
              the valley&quot;.
            </p>
            <p className="m-v-0">
              But the system sees &quot;fruits; apples; fresh&quot;.
            </p>
          </div>
          <div className="c-1-2">
            <img
              className="w-full"
              src="/static/images/apples-oranges-with-hs6.svg "
              alt=""
            />
          </div>
        </div>
        <div className="box box--no-pointer m-t-s">
          <p className="m-t-0 m-b-xs">
            You don&apos;t have to find a perfect match.
          </p>
          <p className="m-v-0">
            Find a close match, then feel free to relabel it.
          </p>
        </div>
      </div>
    )
  }

  const showProduct = () => {
    // When modal is opened - it shows the last selected product
    // rather than jumping directly into search
    return (
      <div className="p-h-s p-t-l">
        <section className="m-b-s body-l">
          <h2 className="h-m p-b-s">Your product</h2>
          <StartEndPage
            commodityCode={selectedProduct.commodity_code || ''}
            defaultCommodityName={
              ReactHtmlParser(selectedProduct.commodity_name).toString() || ''
            }
            saveProduct={saveProduct}
            label="You can rename this to match your exact product"
            buttonLabel="Update product name"
            allowSaveSameName={false}
          />
          <p>
            If you&apos;ve created an Export Plan, make sure you update it to
            reflect your new product. You can change product at any time.
          </p>
          <button
            type="button"
            className="button button--tertiary button--icon"
            onClick={backToSearch}
          >
            <i className="fas fa-arrow-left" />
            Search again
          </button>
        </section>
      </div>
    )
  }

  const searchPages = () => {
    // When in searching mode.  If there are searchResults will show a refinement/result page
    // otherwise the search box page.
    let error = ''
    if (
      searchResults &&
      (!searchResults.txId ||
        (!searchResults.currentQuestionInteraction && !searchResults.hsCode))
    ) {
      error =
        'No results found. Check your spelling and use the search tips below.'
    }
    if (searchResults && searchResults.multiItemError) {
      error = (
        <div>
          <p className="m-t-0">
            We couldn&apos;t find a match because your search had too many
            product names.
          </p>
          <p className="m-b-0">
            Try searching for a broader term or use the search tips below.
          </p>
        </div>
      )
    }
    return !searchResults || error ? (
      searchBox(error)
    ) : (
      <span>
        <button
          type="button"
          className="back-button m-f-s m-t-m"
          onClick={backToSearch}
        >
          <i className="fa fa-arrow-circle-left m-r-xs" />
          Search again
        </button>
        {searchResults && resultsDisplay(searchResults)}
      </span>
    )
  }

  const scrollerClass = `scroll-area ${
    isScrolled && isScrolled.top ? 'scroll-shadow-top' : ''
  } ${isScrolled && isScrolled.bottom ? 'scroll-shadow-bottom' : ''}`
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
          content: {
            maxWidth: '630px',
            left: 'auto',
            right: 'auto',
            overflow: 'hidden',
          },
        }}
      >
        <form className="product-finder text-blue-deep-80">
          <div style={{ height: headerHeight }}>
            {/* nothing in the modal header for the time being */}
          </div>
          <div
            className={scrollerClass}
            style={{ marginTop: headerHeight }}
            onScroll={onScroll}
          >
            <button
              id="dialog-close"
              type="button"
              aria-label="Close"
              className="pull-right m-r-0 dialog-close"
              onClick={closeModal}
            />
            {spinner}
            <div
              className="scroll-inner p-b-m"
              ref={(_scrollInner) => {
                scrollOuter = _scrollInner || scrollOuter
              }}
            >
              {isSearching || !selectedProduct ? searchPages() : showProduct()}
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
  selectedProduct: PropTypes.shape({
    commodity_name: PropTypes.string,
    commodity_code: PropTypes.string,
  }),
}
ProductFinderModal.defaultProps = {
  selectedProduct: null,
}
