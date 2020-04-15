import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import ProductsModal from '@src/views/ProductsModal/Wizard'
import SignupModal from '@src/views/SignupModal/ModalCentreScreen'
import CountriesModal from '@src/views/CountriesModal/Wizard'


export function Base(props){

  const [isProductModalOpen, setIsProductModalOpen] = React.useState(props.isProductModalOpen)
  const [isSignupModalOpen, setIsSignupModalOpen] = React.useState(false)
  const [isCountriesModalOpen, setIsCountriesModalOpen] = React.useState(false)
  const [performSkipFeatureCookieCheck, setPerformSkipFeatureCookieCheck] = React.useState(true)
  const [nextUrl, setNextUrl] = React.useState('')
  const [companySettings, setCompanySettings] = React.useState({expertise_products_services: {other: []}})

  props.productElement.onclick = () => {
    // user is explicitly sking to see the modal, so don't prevent it opening via cookie check
    setIsCountriesModalOpen(false)
    setIsProductModalOpen(true)
    setPerformSkipFeatureCookieCheck(false)
  }
  props.countryElement.onclick = () => {
    // user is explicitly sking to see the modal, so don't prevent it opening via cookie check
    setIsProductModalOpen(false)
    setIsCountriesModalOpen(true)
    setPerformSkipFeatureCookieCheck(false)
  }

  function buildNextUrl(userHasSignupIntent, products) {
    let url = `${location.pathname}?`
    products.forEach(function(product) {
      url += ('products=' + product.value + '&products_label=' + product.label + '&')
    })
    return url
  }

  function onSelectProuctComplete(userHasSignupIntent, products) {
    setIsProductModalOpen(false)
    if (userHasSignupIntent) {
      setCompanySettings({expertise_products_services: {other: products}})
      setIsSignupModalOpen(true)
    } else {
      const url = buildNextUrl(userHasSignupIntent, products)
      window.location.assign(url)
    }
  }

  return (
    <>
      <ProductsModal
        isOpen={isProductModalOpen}
        setIsOpen={setIsProductModalOpen}
        onComplete={onSelectProuctComplete}
        performSkipFeatureCookieCheck={performSkipFeatureCookieCheck}
      />
      <SignupModal
        isOpen={isSignupModalOpen}
        setIsOpen={setIsSignupModalOpen}
        companySettings={companySettings}
        nextUrl={nextUrl}
        performSkipFeatureCookieCheck={performSkipFeatureCookieCheck}
      />
      <CountriesModal
        isOpen={isCountriesModalOpen}
        setIsOpen={setIsCountriesModalOpen}
        performSkipFeatureCookieCheck={performSkipFeatureCookieCheck}
      />
    </>
  )
}


export default function({ element, ...params }) {
  ReactModal.setAppElement(element)

  const mainElement = document.createElement('span');

  element.appendChild(mainElement)

  ReactDOM.render(<Base {...params} />, mainElement)
}
