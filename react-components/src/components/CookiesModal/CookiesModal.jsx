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
        {translations[lang]["Tell us whether you accept cookies"]}
      </h2>
      <p className={`${styles.synopsis} body-text`}>
        {translations[lang]["We use"]}{' '}
        <a
          className="link"
          href={props.privacyCookiesUrl}
          ref={(_firstLink) => (firstLink = _firstLink)}
        >
          {translations[lang]["cookies to collect information"]}
        </a>{' '}
          {translations[lang]["about how you use great.gov.uk. We use this information to make the website work as well as possible and improve government services."]}
      </p>
      <div className={styles.buttonContainer}>
        <a
          className={`${styles.button} button primary-button`}
          href="#"
          onClick={handleAcceptAllCookies}
        >
          {translations[lang]["Accept all cookies"]}
        </a>
        <span className={styles.buttonSeperator} />
        <a
          className={`${styles.button} button primary-button`}
          href={props.preferencesUrl + window.location.search}
        >
          {translations[lang]["Set cookie preferences"]}
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
