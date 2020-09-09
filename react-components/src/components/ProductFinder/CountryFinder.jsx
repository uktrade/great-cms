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
    width: '100%',
    padding: '0',
    border: 'none',
  },
  overlay: {
    background: 'rgb(45 45 45 / 45%)',
    zIndex: '3',
  },
}


export function CountryFinder(props) {
  var searchInput
  const [modalIsOpen, setIsOpen] = React.useState(false)
  const [selectedCountry, setSelectedCountry] = React.useState(props.text)

  function openModal() {
    setIsOpen(true)
  }

  function closeModal() {
    setIsOpen(false)
  }

  function modalAfterOpen() {
    //searchInput.focus()
  }

  function saveCountry(country) {
    setSelectedCountry(country);
    let result = Services.updateExportPlan({export_countries:[country]}).then((result) => {
      closeModal();
      // window.location.reload(true);   # do we need to reload page
    }).catch((result) => {
      debugger;
    });    
  }

  function selectCountry(evt) {
    let targetCountry = evt.target.getAttribute('data-country');
    saveCountry(targetCountry);
  }

  return (
    <span>
      <button className="button button--primary button--round-corner" onClick={openModal}>
        {selectedCountry}
      </button>
      <ReactModal isOpen={modalIsOpen} onRequestClose={closeModal} style={customStyles} onAfterOpen={modalAfterOpen}>
        <form className="country-chooser">
            <button className="pull-right m-r-0" onClick={closeModal}>
              <span className="fa fa-window-close"></span>
            </button>
            <h3 className="h-m p-t-0">Choose your country</h3>
            <div  className="country-list" onClick={selectCountry}> 
              <button type="button" className="link" data-country="France">France</button>
              <button type="button" className="link" data-country="Belgium">Belgium</button>
              <button type="button" className="link" data-country="Brazil">Brazil</button>
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
  ReactDOM.render(<CountryFinder text={params.element.innerText}></CountryFinder>, params.element)
}
