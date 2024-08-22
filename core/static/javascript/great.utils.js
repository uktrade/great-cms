GreatFrontend = window.GreatFrontend || {}

GreatFrontend.utils = {
  showElement: (el) => {
    el.style.display = 'block'
  },
  hideElement: (el) => {
    el.style.display = 'none'
  },
  hasUserConsentedToTracking: () => {
    let hasUserConsented = false
    const cookiesArray = document.cookie.split('; ')
  
    cookiesArray.forEach((cookieString) => {
      if (
        cookieString.includes('cookies_policy') &&
        cookieString.includes('"usage":true')
      ) {
        hasUserConsented = true
      }
    })
  
    return hasUserConsented
  }
}