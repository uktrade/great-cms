import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'
import CookieManager from '../../directory_components/static/directory_components/js/dit.components.cookie-notice'

import styles from './CookiesModal.css'

export function CookiesModal(props) {
  let firstLink;
  const [isOpen, setIsOpen] = React.useState(props.isOpen)
  const focusTrap = React.useRef(false);

  function hanleAcceptAllCookies(event) {
    CookieManager.acceptAllCookiesAndShowSuccess(event);
    window.location.reload(false);
    setIsOpen(false);
  }

  const handleFocusChange = (evt) => {
    if (focusTrap.current) {
      let modal = evt.target.closest('.ReactModal__Content');
      if ((!modal || (modal == evt.target)) && firstLink) {
        firstLink.focus();
      }
    } else {
      focusTrap.current = true;
    }
  }

  React.useEffect(() => {
    document.body.addEventListener('focusin', handleFocusChange);
    return () => {
      document.body.removeEventListener('focusin', handleFocusChange);
    };
  }, []);

  return (
    <Modal
      isOpen={isOpen}
      contentLabel="Cookies consent manager"
    >
      <h2 className={`${styles.heading} heading-medium`}>Tell us whether you accept cookies</h2>
      <p className={`${styles.synopsis} body-text`} >
        We use <a
          className="link"
          href={props.privacyCookiesUrl}
          ref={(_firstLink) => (firstLink = _firstLink)}
        >cookies to collect information</a> about how you use great.gov.uk. We use this information to make the website work as well as possible and improve government services.
      </p>
      <div className={styles.buttonContainer}>
        <a className={`${styles.button} button`} href="#" onClick={hanleAcceptAllCookies}>Accept all cookies</a>
        <span className={styles.buttonSeperator}></span>
        <a className={`${styles.button} button`} href={props.preferencesUrl + window.location.search}>Set cookie preferences</a>
      </div>
    </Modal>
  )
}

CookiesModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  preferencesUrl: PropTypes.string.isRequired,
}

export default function createCookiesModal({ element, ...params }) {
  Modal.setAppElement(element)
  ReactDOM.render(<CookiesModal {...params} />, element)
}
