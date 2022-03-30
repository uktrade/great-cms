import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'
import { analytics } from '@src/Helpers'
import CookieManager from './dit.components.cookie-notice'

import styles from './CookiesModal.css'

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

  React.useEffect(() => {
    document.body.addEventListener('focusin', handleFocusChange)
    return () => {
      document.body.removeEventListener('focusin', handleFocusChange)
    }
  }, [])

  return (
    <Modal isOpen={isOpen} contentLabel="Cookies consent manager">
      <h2 className={`${styles.heading} heading-medium`}>
        Tell us whether you accept cookies
      </h2>
      <p className={`${styles.synopsis} body-text`}>
        We use{' '}
        <a
          className="link"
          href={props.privacyCookiesUrl}
          ref={(_firstLink) => (firstLink = _firstLink)}
        >
          cookies to collect information
        </a>{' '}
        about how you use great.gov.uk. We use this information to make the
        website work as well as possible and improve government services.
      </p>
      <div className={styles.buttonContainer}>
        <a
          className={`${styles.button} button`}
          href="#"
          onClick={handleAcceptAllCookies}
        >
          Accept all cookies
        </a>
        <span className={styles.buttonSeperator} />
        <a
          className={`${styles.button} button`}
          href={props.preferencesUrl + window.location.search}
        >
          Set cookie preferences
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
