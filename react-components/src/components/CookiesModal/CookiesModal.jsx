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

  function handleRejectAllCookies(event) {
    CookieManager.rejectAllCookiesAndShowSuccess(event)

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
  let lang = props.lang ? props.lang.substring(0, 2) : 'en'

  // in the normal flow there should never be an invalid language code
  // because django will fallback to site default. including below to
  // ensure cookie modal is self-contained
  if (!Object.keys(translations).includes(lang)) {
    lang = 'en'
  }

  React.useEffect(() => {
    document.body.addEventListener('focusin', handleFocusChange)
    return () => {
      document.body.removeEventListener('focusin', handleFocusChange)
    }
  }, [])

  return (
    <Modal isOpen={isOpen} contentLabel="Cookies on Business.gov.uk">
      <div className="great">
        <h2 aria-hidden="true" className={`govuk-heading-m`}>
          {translations[lang]['Cookies on Business.gov.uk']}
        </h2>
      </div>
      <p className={`${styles.synopsis}`}>{translations[lang]['We use']} </p>
      <div className={`${styles.buttonContainer} great great-overflow-visible`}>
        <button
          className={`${styles.greatButton} govuk-button`}
          onClick={handleAcceptAllCookies}
        >
          {translations[lang]['Accept additional cookies']}
        </button>
        <button
          className={`${styles.greatButton} govuk-button`}
          onClick={handleRejectAllCookies}
        >
          {translations[lang]['Reject additional cookies']}
        </button>
        <div className={`${styles.cookieLink}`}>
          <a
            className={`govuk-link govuk-!-margin-bottom-1`}
            href={props.preferencesUrl + window.location.search}
          >
            {translations[lang]['View cookies']}
          </a>
        </div>
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
