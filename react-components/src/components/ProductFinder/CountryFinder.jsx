import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { getModalIsOpen, getProductsExpertise } from '@src/reducers'
import Services from '@src/Services'

const customStyles = {
  content: {
    top: '10%',
    left: '10%',
    width: '80%',
    border: 'none',
    height: '80%',
    padding: '40px 60px',
  },
  overlay: {
    background: 'rgb(45 45 45 / 45%)',
    zIndex: '3',
  },
}

//const countries = ['Algeria', 'Angola', 'Benin', 'Botswana', 'Belize', 'Burkina Faso', 'Burundi', 'Cameroon', 'Cape Verde', 'Central African Republic' ];
const suggested = ['France', 'Spain', 'Italy', 'Jamaica'];

export function CountryFinder(props) {
  let modalContent;
  const [modalIsOpen, setIsOpen] = React.useState(false);
  const [selectedCountry, setSelectedCountry] = React.useState(props.text);
  const [countryList, setCountryList] = React.useState()

  const openModal = () => {
    setIsOpen(true);
  }

  const closeModal = () => {
    setIsOpen(false);
  }

  const modalAfterOpen = () => {
    modalContent.style.maxHeight = '700px';
    if (!countryList) {
      getCountries();
    }
  }

  const getCountries = () => {
    Services.getCountries().then((result) => {
      // map regions
      let regions = {};
      for (const [index, country] of result.entries()) {
        let region = country.region;
        (regions[region] = regions[region] || []).push(country);
      }
      setCountryList(regions);
    });
  }

  const saveCountry = (country) => {
    setSelectedCountry(country);
    let result = Services.updateExportPlan({ export_countries: [country] }).then((result) => {
      closeModal();
    }).catch((result) => {
      // TODO: Add error confirmation here
    });
  }

  const selectCountry = (evt) => {
    let targetCountry = evt.target.getAttribute('data-country');
    saveCountry(targetCountry);
  }

  let _regions = Object.keys(countryList || {}).map((region) => {
    let _countries = (countryList[region] || []).map((country, index) => {
      return (<li style={{order:'5'}} key={country.id}><button type="button" className="link m-r-s m-b-xs" data-country={country.name}>{country.name}</button></li>)
    })
    return <section key={region}>
      <div className="grid" >
        <div className="c-full-width">
          <h2 class="h-s">{region}</h2>
          <ul style={{display:'flex', flexWrap:'wrap'}}>{_countries}</ul>
        </div>
      </div>
      </section>
  })

  const _suggested = [];
  for (const [index, value] of suggested.entries()) {
    _suggested.push(<button key={index} type="button" className="button button--tertiary button--round-corner m-r-s" data-country={value}>{value}</button>);
  }

  return (
    <span>
      <button className="button button--primary button--round-corner" onClick={openModal}>
        {selectedCountry}
      </button>
      <ReactModal 
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
        onAfterOpen={modalAfterOpen}
        contentRef={(_modalContent) => (modalContent = _modalContent)}
      >
        <form className="country-chooser">
          <button className="pull-right m-r-0" onClick={closeModal}>
            <span className="fa fa-window-close"></span>
          </button>
          <h2 className="h-l p-t-0">Choose a target market</h2>

          <h3 className="h-m p-t-0">Suggested markets for your product</h3>
          <p className="body-m">These markets may be a good place to consider exporting your product</p>
          <ul className="" onClick={selectCountry}>
            {_suggested }
          </ul>
          <hr className="bg-black-70"></hr>
          
          <h3 className="h-m p-t-0">Use our data to compare markets</h3>
          <div className="grid">
            <div className="c-3-4"><p className="body-m">Compare facts and figures for over 180 countries to help you determine which will be the best fit for your product.</p></div>
            <div className="c-1-4"><a href="#" className="button button--secondary pull-right width-full">Find your market</a></div>
          </div>

          <hr className="bg-black-70"></hr>
          <h3 className="h-m p-t-0">Select a target market</h3>
          <ul  className="country-list body-m" onClick={selectCountry}>
            { _regions }
          </ul>

        </form>
      </ReactModal>
    </span>
  )
}

export default function({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  ReactDOM.render(<CountryFinder text={params.element.innerText}></CountryFinder>, params.element)
}