import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'
import { analytics } from '@src/Helpers'
import CookieManager from './dit.components.cookie-notice'

import styles from './CookiesModal.css'
import translations from './translations/CookiesModalTranslations.json'

export function CookiesModal(props) {
  let firstLink
  const [isOpen, setIsOpen] = React.useState(
    CookieManager.getPreferencesCookie() === null
  )
  const focusTrap = React.useRef(false)

  function handleAcceptAllCookies(event) {
    CookieManager.acceptAllCookiesAndShowSuccess(event)

    analytics({ event: 'cookies_policy_accept' })
    analytics({ event: 'gtm.dom' })

    setIsOpen(false)
  }

  const handleFocusChange = (evt) => {
    if (focusTrap.current) {
      const modal = evt.target.closest('.ReactModal__Content')
      if ((!modal || modal == evt.target) && firstLink) {
        firstLink.focus()
      }
    } else {
      focusTrap.current = true
    }
  }

  // here we are ignoring the locale part of a language short code
  // as they are not currently implemented in the .json file of translations
  let lang = props.lang ? props.lang.substring(0,2) : 'en'

  // in the normal flow there should never be an invalid language code
  // because django will fallback to site default. including below to
  // ensure cookie modal is self-contained
  if (! Object.keys(translations).includes(lang)){
    lang = 'en'
  }

  React.useEffect(() => {
    document.body.addEventListener('focusin', handleFocusChange)
    return () => {
      document.body.removeEventListener('focusin', handleFocusChange)
    }
  }, [])

  return (
    <Modal isOpen={isOpen} contentLabel="Cookies consent manager">
      <h2 className={`${styles.heading} heading-medium`}>
        {translations[lang]["Cookies on great.gov.uk"]}
      </h2>
      <p className={`${styles.synopsis} body-text`}>
        {translations[lang]["We use"]}{' '}
      </p>
      <div className={`${styles.buttonContainer} great`}>
        <a
          className={`${styles.greatButton} govuk-button`}
          href="#"
          onClick={handleAcceptAllCookies}
        >
          {translations[lang]["Accept additional cookies"]}
        </a>
        <a
          className={`govuk-link govuk-!-margin-bottom-1`}
          href={props.preferencesUrl + window.location.search}
        >
          {translations[lang]["View cookies"]}
        </a>
      </div>
    </Modal>
  )
}

CookiesModal.propTypes = {
  preferencesUrl: PropTypes.string.isRequired,
}

export default function createCookiesModal({ element, ...params }) {
  Modal.setAppElement(element)
  ReactDOM.render(<CookiesModal {...params} />, element)
}
