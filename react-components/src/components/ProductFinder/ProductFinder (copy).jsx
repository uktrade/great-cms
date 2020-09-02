import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import Select, { components } from 'react-select' 
//import { connect, Provider } from 'react-redux'
import { getModalIsOpen, getProductsExpertise } from '@src/reducers'
import Services from '@src/Services'
//import actions from '@src/actions'

const customStyles = {
  content: {
    top: '0',
    right: '0',
    bottom: '0',
    left: 'auto',
    minWidth: '600px',
    maxWidth: '900px',
    padding: '0',
    border: 'none',
  },
  overlay: {
    //position: 'absolute',
    background: 'rgb(45 45 45 / 45%)',
    zIndex: '3',
  },
}

export function ProductFinder(props) {
  var searchInput
  const [modalIsOpen, setIsOpen] = React.useState(false)
  const [searchResults, setSearchResults] = React.useState([])

  function openModal() {
    setIsOpen(true)
  }

  function closeModal() {
    setIsOpen(false)
  }

  function inputKeypress(evt) {
    if (evt.key == 'Enter') {
      evt.preventDefault()
      search()
    }
  }

  function search() {
    let query = searchInput.value
    Services.lookupProduct({ q: query }).then(
      (result) => {
        console.log('***   result', result)
        setSearchResults(result && result.data)
      })
      .catch(() => {
        setSearchResults(result || {})
      })
  }

  function changeOption(evt) {
    let txId = searchResults.txId;
    let interractionId = evt.target.getAttribute('data-key');
    let valueId = evt.target.value;
    let valueString = evt.target.options[evt.target.selectedIndex].text;
    Services.lookupProductRefine({txId, interractionId, valueId, valueString}).then(
      (result) => {
        console.log('***   refine result', result)
        if (result && result.data && result.data.txId) {
          setSearchResults(result && result.data)
        } else {
          setSearchResults(searchResults); // force re-render to reset any changed selectors
        }
      })
      .catch((error) => {
        debugger;
        setSearchResults({})
      })
  }

  function renderOption(option, unselectedString) {
    //let label = (option.name == 'other' ? 'Other '+unselectedString : option.name);
    return (
      <option key={option.id} value={option.id} selected={option.value == 'true'}>
        {option.name}
      </option>
    )
  }

  function Attribute(attribute) {
    let selectedOption = null;
    let options = (attribute.attrs || []).map((option, index) => {
      var ret = {value: option.value, label:option.name};
      if(option.value == 'true') {
        selectedOption = ret;
      }
      return ret;
      //renderOption(option, attribute.unselectedString)
    })
    console.log('selectedValue', selectedOption)
    return( 
      <div className="grid" key={attribute.id}>
        <div className="c-1-3 p-t-xs">{attribute.label}</div>
        <div className="c-1-3">
          <Select className="form-control" onChange={changeOption} data-key={attribute.id} value={selectedOption} options={options}>
          </Select>
        </div>
        <div className="c-1-3 p-t-xs">{attribute.unselectedString}</div>
      </div>
    )   
  }

  function Section(title, sectionDetails) {
    if (!sectionDetails || sectionDetails.length == 0 || !sectionDetails.map) return null;
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
        add product
      </button>
      <ReactModal isOpen={modalIsOpen} onRequestClose={closeModal} style={customStyles} contentLabel="Example Modal">
        <form className="product-finder">
          <div className="search-header bg-blue-deep-80 text-white p-s">
            <button className="pull-right m-r-s" onClick={closeModal}>
              <span className="fa fa-window-close"></span>
            </button>
            <h3 className="h-m text-white p-t-0">Search by name</h3>
            <div>Find the product you want to export</div>
            <input
              className="form-control c-2-3"
              type="text"
              ref={(_searchInput) => (searchInput = _searchInput)}
              onKeyPress={inputKeypress}
            />
            <button className="button button--tertiary m-f-xxs" type="button" onClick={search}>
              Search
            </button>
          </div>
          <div className="classification-result">
            {searchResults.hsCode && (
              <section className="found-section grid bg-black-10">
                  <div className="c-1-3"><span className="h-m">Here's your product</span></div>
                  <div className="c-1-3 bold">{searchResults.productDescription}</div>
                  <div className="c-1-3">hs code: <span className="bold">{searchResults.hsCode}</span></div>
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
            {Section('Please choose your item', searchResults.currentItemInteraction && [searchResults.currentItemInteraction])}
            {!searchResults.currentItemInteraction && Section(
              'Tell us more about "'+searchResults.productDescription+'"',
              searchResults.currentQuestionInteraction && [searchResults.currentQuestionInteraction]
            )}
            {Section("Your item's characteristics:", searchResults.knownInteractions)}
            {Section("We've assumed:", searchResults.assumedInteractions)}
          </div>
        </form>
      </ReactModal>
    </span>
  )
}
/*
const mapStateToProps = (state) => {
  return {
    isDialogueOpen: getModalIsOpen(state, 'products'),
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    setDialogueOpen: (isOpen) => {
      dispatch(actions.toggleModalIsOpen('products', isOpen))
    },
  }
}

const ModalContainer = connect(mapStateToProps, mapDispatchToProps)(ProductFinder)
*/
/*
export default function ({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  params.element.onClick=openModal;
  Modal.setAppElement(mainElement)
  ReactDOM.render(
    <Provider store={Services.store}>
      <ProductFinder {...params} />
    </Provider>,
    mainElement
  )
}*/

export default function ({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  ReactDOM.render(<ProductFinder></ProductFinder>, params.element)
}
