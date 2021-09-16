import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'
import Slider from 'react-slick'
import Services from '@src/Services'
import {
  useUserProducts,
  useActiveProduct,
} from '@src/components/hooks/useUserData'
import { analytics, capitalize } from '@src/Helpers'
import Spinner from '../Spinner/Spinner'
import Interaction from './Interaction'
import ValueInteraction from './ValueInteraction'
import SearchInput from './SearchInput'
import StartEndPage from './StartEndPage'

export default function ProductFinderModal(props) {
  const { modalIsOpen, setIsOpen, onCloseRedirect, onAddProduct } = props

  let scrollOuter
  const [searchResults, setSearchResults] = useState()
  const [isLoading, setLoading] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showingInteraction, setShowingInteraction] = useState()
  const { products, setProducts, loadProducts } = useUserProducts(false)
  const [activeProduct, setActiveProduct] = useActiveProduct(false)

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
    setSearchResults()
  }

  const modalAfterOpen = () => {
    setIsScrolled({})
    setSearchTerm('')
    loadProducts()
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

  const sliderSettings = {
    centerMode: true,
    centerPadding: '20px',
    dots: true,
    arrows: false,
    infinite: false,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
  }

  const saveProduct = (commodityCode, commodityName) => {
    const newProduct = {
      commodity_name: commodityName,
      commodity_code: commodityCode,
    }
    setProducts([...products, newProduct])
    setActiveProduct(newProduct)
    onAddProduct(newProduct)
    if (searchResults) {
      analytics({
        event: 'addProductSuccess',
        productKeyword: commodityName,
        productCode: commodityCode,
      })
      closeModal()
    }
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
      <section className="m-h-s m-b-s">
        <div className="h-m p-b-s">Match found</div>
        <StartEndPage
          commodityCode={_searchResults.hsCode}
          defaultCommodityName={capitalize(_searchResults.currentItemName)}
          saveProduct={saveProduct}
          searchCompletedMode
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
          <section className="m-h-s body-s">
            Product classification data API provided by 3CE.
          </section>
        </div>
      )

    return sections
  }

  const infoCards = [
    {
      className: 'box box--no-pointer m-t-s',
      content: (
        <p>
          When you search for a product you may have to answer a few questions
          before you find a match.
        </p>
      ),
    },
    {
      className: 'box box--no-pointer m-t-s',
      content: (
        <>
          <p className="m-t-0 m-b-xs">
            This is because we use HS (
            <span className="body-l-b">harmonised system</span>) codes to
            classify goods.
          </p>
          <p className="m-v-0">
            Think of it like the folder structure on a computer.
          </p>
        </>
      ),
    },
    {
      className: 'box box--no-pointer m-t-s inline-block',
      content: (
        <>
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
        </>
      ),
    },
    {
      className: 'box box--no-pointer m-t-s',
      content: (
        <>
          <p className="m-t-0 m-b-xs">
            You don&apos;t have to find a perfect match.
          </p>
          <p className="m-v-0">
            Find a close match, then feel free to relabel it.
          </p>
        </>
      ),
    },
  ]

  const renderInfoCards = () => {
    return infoCards.map((card, idx) => (
      <div key={`card-${idx}`} className={card.className}>
        {card.content}
      </div>
    ))
  }

  const searchBox = (error) => {
    return (
      <div className="p-h-s p-t-l">
        <h3 className="h-m p-t-0 p-b-xxs">
          <label htmlFor="search-input">Find product</label>
        </h3>
        <span className="visually-hidden">
          Type the name of your product eg: fresh strawberries
        </span>
        {error && <div className="form-group-error p-v-xs m-v-xs">{error}</div>}
        <div className="flex-centre m-t-xs search-input">
          <SearchInput
            id="search-input"
            onChange={setSearchTerm}
            onKeyReturn={search}
            autoFocus
            iconClass="fa-search"
            placeholder="ie: fresh strawberries"
            ariaDescribedby="search-hint"
          />
          <button
            className="search-button button button--small button--only-icon m-f-xs"
            disabled={!searchTerm}
            type="button"
            onClick={search}
            aria-label="search item"
          >
            <span className="visually-hidden">Search product</span>
            <i className="fa fa-arrow-right" />
          </button>
        </div>
        {/* Desktop rendering with info cards displayed as a stack  */}
        <div className="only-desktop">{renderInfoCards()}</div>
        {/* Mobile rendering with info cards displayed within a carousel  */}
        <div className="only-mobile">
          <Slider {...sliderSettings}>{renderInfoCards()}</Slider>
        </div>
      </div>
    )
  }
  /* TODO: Left here because we are surely going to need a display and rename function for products
     once the designers realise it's now missing.

  const showProduct = () => {
    // When modal is opened - it shows the last selected product
    // rather than jumping directly into search
    return (
      <div className="p-h-s p-t-l">
        <section className="m-b-s">
          <h2 className="h-m p-b-s">Your product</h2>
          <StartEndPage
            commodityCode={products.commodity_code || ''}
            defaultCommodityName={
              ReactHtmlParser(selectedProduct.commodity_name).toString() || ''
            }
            saveProduct={saveProduct}
            label="You can rename this to match your exact product"
            buttonLabel="Update product name"
            allowSaveSameName={false}
          />
          <button
            type="button"
            className="button button--primary m-t-s"
            onClick={backToSearch}
          >
            Search again
          </button>
        </section>
      </div>
    )
  }
*/
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
          <i className="fa fa-arrow-circle-left" />
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
        className="modal centre-modal-content p-v-s p-h-l"
        overlayClassName="modal-overlay center"
        onAfterOpen={modalAfterOpen}
        shouldCloseOnOverlayClick={false}
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
              tabIndex="0"
              ref={(_scrollInner) => {
                scrollOuter = _scrollInner || scrollOuter
              }}
            >
              {searchPages()}
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
  onCloseRedirect: PropTypes.string,
  onAddProduct: PropTypes.func,
}
ProductFinderModal.defaultProps = {
  onCloseRedirect: '',
  onAddProduct: () => 0,
}
