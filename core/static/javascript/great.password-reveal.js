GreatFrontend = window.GreatFrontend || {}

GreatFrontend.PasswordInput = {
  init: () => {
    const passwordInput = document.getElementById('password-input');
    const passwordShowButton = document.getElementById('password-show-button');
    const hiddenClass= 'great-hidden'
    const visuallyHiddenClass= 'great-visually-hidden'

    const show = () => {
        setType('text')
        screenReaderStatusMessage.innerText='Your password is visible'
        passwordShowButton.innerHTML='Hide'
        passwordShowButton.ariaLabel='Hide password'
    }

    const hide = () => {
        setType('password')
        screenReaderStatusMessage.innerText='Your password is hidden'
        passwordShowButton.innerHTML='Show'
        passwordShowButton.ariaLabel='Show password'
    }

    const setType = (type) => {
        passwordInput.setAttribute('type', type)
    }
    passwordShowButton.classList.remove(hiddenClass);

    const screenReaderStatusMessage = document.createElement('div')
    screenReaderStatusMessage.className = visuallyHiddenClass
    screenReaderStatusMessage.setAttribute('aria-live', 'polite')
    passwordShowButton.insertAdjacentElement('afterend', screenReaderStatusMessage)

    passwordShowButton.addEventListener('click', (event) => {
        event.preventDefault()
        if (passwordInput.type === 'password') {
            show()
        }
        else {
            hide()
        }
    })

    if (passwordInput.form) {
        passwordInput.form.addEventListener('submit', () => hide())
      }

      // If the page is restored from bfcache and the password is visible, hide it again
    window.addEventListener('pageshow', (event) => {
    if (event.persisted && passwordInput.type !== 'password') {
        hide()
    }
    })

    // Default the component to having the password hidden.
    hide()


    }

}
