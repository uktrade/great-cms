const MESSAGE_UNEXPECTED_ERROR = {'__all__': ['Unexpected Error']}
const MESSAGE_INCORRECT_CREDENTIALS = {'__all__': ['Incorrect username or password']}


const post = function(url, data) {
  console.log(url)
  console.log(data)
  console.log(config.csrfToken)
  return fetch(url, {
    method: 'post',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': config.csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(data),
  })
}


const createUser = function({username, password}) {
  return post(config.signupUrl, {username, password}).then(response => {
    if (response.status == 400) {
      return response.json().then(error => { throw error })
    } else if (response.status != 200) {
      throw MESSAGE_UNEXPECTED_ERROR
    }
  })
}


const checkVerificationCode = function({ username, code}) {
  return post(config.verifyCodeUrl, {username, code}).then(response => {
    if (response.status == 400) {
      return response.json().then(error => { throw error })
    } else if (response.status != 200) {
      throw MESSAGE_UNEXPECTED_ERROR
    }
  })
}

const checkCredentials = function({ username, password }) {
  return post(config.loginUrl, {username, password}).then(response => {
    if (response.status == 400) {
      throw MESSAGE_INCORRECT_CREDENTIALS
    } else if (response.status != 200) {
      throw MESSAGE_UNEXPECTED_ERROR
    }
  })
}

// static values that will not change during execution of the code
let config = {}
const setConfig = function({
  loginUrl,
  signupUrl,
  verifyCodeUrl,
  csrfToken,
  linkedInUrl,
  googleUrl,
  termsUrl
}) {
  config.loginUrl = loginUrl
  config.signupUrl = signupUrl
  config.verifyCodeUrl = verifyCodeUrl
  config.csrfToken = csrfToken
  config.linkedInUrl = linkedInUrl
  config.googleUrl = googleUrl
  config.termsUrl = termsUrl
}

export default {
  createUser,
  checkCredentials,
  checkVerificationCode,
  setConfig,
  config,
  messages: {
    MESSAGE_UNEXPECTED_ERROR,
    MESSAGE_INCORRECT_CREDENTIALS,
  }
}