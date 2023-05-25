export const isAddVideoPage = (pathname) =>
  pathname === '/admin/media/video/add/'

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
