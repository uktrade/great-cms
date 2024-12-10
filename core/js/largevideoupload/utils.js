export const isAddVideoPage = (pathname) =>
  pathname === '/admin/media/video/add/'

export const isAddMultipleDocument = (pathname) =>
  pathname === '/admin/documents/multiple/add/'

export const isEditVideoPage = (pathname) =>
  pathname.includes('/admin/media/edit/')

export const isMediaChooserPage = (document) =>
  document.querySelector("[data-chooser-url='/admin/media/chooser/']")

export const showHideElements = (show, hide, display = 'block') => {
  document.querySelector(show).style.display = display
  document.querySelector(hide).style.display = 'none'
}

export const createElement = (el, options = []) => {
  const _el = document.createElement(el)

  if (_el) {
    options.forEach(({ key, val }) => {
      _el[key] = val
    })

    return _el
  }

  return document.createElement('div')
}

export const isFormValid = (file) => {
  const titleVal = document.querySelector('#id_title').value
  const fileNameLength = file.name.length
  const englishSubtitlesVal = document.querySelector('#id_subtitles_en').value

  const isTitleValid = titleVal !== ''
  const isFileNameValid = fileNameLength <= 100
  const isEnglishSubtitleValid =  englishSubtitlesVal !== ''

  const isValid = isTitleValid && isFileNameValid && isEnglishSubtitleValid

  if (isValid) {
    document.querySelector('.messages').innerHTML = ''
    return true
  }

  const fields = [
    {
      isValid: isTitleValid,
      field: 'title',
      errorMessage: ' This field is required.',
    },
    {
      isValid: isFileNameValid,
      field: 'file',
      errorMessage: ' Filename cannot exceed 100 characters.',
    },
    {
      isValid: isEnglishSubtitleValid,
      field: 'subtitles_en',
      errorMessage: ' This field is required.',
    },
  ]

  fields.forEach(({ isValid, field, errorMessage }) => {
    let errorMessageP = document.querySelector(
      `[data-contentpath="${field}"] .w-field__errors p`
    )
    let errorMessageSVG = document.querySelector(
      `[data-contentpath="${field}"] .w-field__errors svg`
    )

    if (isValid) {
      document
        .querySelector(`[data-contentpath="${field}"]`)
        .classList.remove('w-field--error')

      if (errorMessageP) {
        errorMessageP.remove()
      }

      if (errorMessageSVG) {
        errorMessageSVG.remove()
      }
    } else {
      document
        .querySelector(`[data-contentpath="${field}"]`)
        .classList.add('w-field--error')

      if (errorMessageP) {
        errorMessageP.innerHTML = errorMessage
      } else {
        const p = document.createElement('p')
        p.classList.add('error-message')
        p.innerHTML = errorMessage
        document
          .querySelector(`[data-contentpath="${field}"] .w-field__errors`)
          .append(p)
      }
    }
  })

  document.querySelector('.messages').innerHTML =
    '<ul><li class="error"><svg class="icon icon-warning messages-icon" aria-hidden="true"><use href="#icon-warning"></use></svg>The media file could not be saved due to errors.</li></ul>'

  return false
}

export const scrollToTopOfPage = (document) => {
  document.querySelector('#main').scrollTo({
    top: 0,
    left: 0,
    behavior: 'smooth',
  })
}
