const MESSAGE_UNEXPECTED_ERROR = {'__all__': ['Unexpected Error']}
const MESSAGE_INCORRECT_CREDENTIALS = {'__all__': ['Incorrect username or password']}
const MESSAGE_PERMISSION_DENIED = {'__all__': ['You do not have permission to perform this action']}


const post = function(url, data) {
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


const createUser = function({email, password}) {
  return post(config.signupUrl, {email, password}).then(responseHandler)
}


const checkVerificationCode = function({ email, code}) {
  return post(config.verifyCodeUrl, {email, code}).then(responseHandler)
}

const checkCredentials = function({ username, password }) {
  return post(config.loginUrl, {username, password}).then(response => {
    if (response.status == 400) {
      throw MESSAGE_INCORRECT_CREDENTIALS
    } else {
      return responseHandler(response)
    }
  })
}

const enrolCompany = function({ company_name, expertise_industries, expertise_countries, first_name, last_name }) {
  const data = { company_name, expertise_industries, expertise_countries, first_name, last_name }
  return post(config.enrolCompanyUrl, data).then(responseHandler)
}

const responseHandler = function(response) {
  if (response.status == 400) {
    return response.json().then(error => { throw error })
  } else if (response.status == 403) {
    throw MESSAGE_PERMISSION_DENIED
  } else if (response.status != 200) {
    throw MESSAGE_UNEXPECTED_ERROR
  }
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
  termsUrl,
  enrolCompanyUrl,
  industryOptions,
}) {
  config.loginUrl = loginUrl
  config.signupUrl = signupUrl
  config.verifyCodeUrl = verifyCodeUrl
  config.csrfToken = csrfToken
  config.linkedInUrl = linkedInUrl
  config.googleUrl = googleUrl
  config.termsUrl = termsUrl
  config.enrolCompanyUrl = enrolCompanyUrl
  config.industryOptions = industryOptions
}

export default {
  createUser,
  checkCredentials,
  checkVerificationCode,
  enrolCompany,
  setConfig,
  config,
  messages: {
    MESSAGE_UNEXPECTED_ERROR,
    MESSAGE_INCORRECT_CREDENTIALS,
  }
}