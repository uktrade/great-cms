const MESSAGE_UNEXPECTED_ERROR = {'__all__': ['Unexpected Error']}
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
  return post(config.apiSignupUrl, {email, password}).then(responseHandler)
}


const checkVerificationCode = function({ email, code}) {
  return post(config.verifyCodeUrl, {email, code}).then(responseHandler)
}


const checkCredentials = function({ email, password }) {
  return post(config.apiLoginUrl, {email, password}).then(responseHandler)
}


const enrolCompany = function({ company_name, expertise_industries, expertise_countries, first_name, last_name }) {
  const data = { company_name, expertise_industries, expertise_countries, first_name, last_name }
  return post(config.enrolCompanyUrl, data).then(responseHandler)
}


const updateCompany = function({ company_name, expertise_industries, expertise_countries, first_name, last_name }) {
  const data = { company_name, expertise_industries, expertise_countries, first_name, last_name }
  return post(config.apiUpdateCompanyUrl, data).then(responseHandler)
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
  apiLoginUrl,
  apiSignupUrl,
  apiUpdateCompanyUrl,
  countryOptions,
  csrfToken,
  dashboardUrl,
  enrolCompanyUrl,
  googleUrl,
  industryOptions,
  linkedInUrl,
  loginUrl,
  passwordResetUrl,
  termsUrl,
  verifyCodeUrl,
}) {
  config.apiLoginUrl = apiLoginUrl
  config.apiSignupUrl = apiSignupUrl
  config.apiUpdateCompanyUrl = apiUpdateCompanyUrl
  config.countryOptions = countryOptions
  config.csrfToken = csrfToken
  config.dashboardUrl = dashboardUrl
  config.enrolCompanyUrl = enrolCompanyUrl
  config.googleUrl = googleUrl
  config.industryOptions = industryOptions
  config.linkedInUrl = linkedInUrl
  config.loginUrl = loginUrl
  config.passwordResetUrl = passwordResetUrl
  config.termsUrl = termsUrl
  config.verifyCodeUrl = verifyCodeUrl
}

export default {
  createUser,
  checkCredentials,
  checkVerificationCode,
  enrolCompany,
  updateCompany,
  setConfig,
  config,
  messages: {
    MESSAGE_UNEXPECTED_ERROR,
    MESSAGE_PERMISSION_DENIED,
  }
}