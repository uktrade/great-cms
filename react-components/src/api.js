/* eslint-disable */
import { config } from '@src/config'
import { messages } from '@src/constants'

const post = function (url, data) {
  return fetch(url, {
    method: 'post',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': config.csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(data),
  })
}

const httpDelete = function (url, data) {
  return fetch(url, {
    method: 'delete',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': config.csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(data),
  })
}

const get = function (url, params) {
  const parsedUrl = new URL(`${location.origin}${url}`)
  const parsedParams = new URLSearchParams(params).toString()
  parsedUrl.search = parsedParams

  return fetch(parsedUrl, {
    method: 'get',
    cache: 'no-store',
    headers: {
      Accept: 'application/json',
      'X-CSRFToken': config.csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
}

async function greatApi(url, data, method = 'GET') {
  // GET method can't have a body
  const body = method !== 'GET' ? { body: JSON.stringify(data) } : {}
  return await fetch(url, {
    method,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': config.csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
    ...body,
  })
}

const responseHandler = function (response) {
  if (response.status == 400) {
    return response.json().then((error) => {
      throw error
    })
  } else if (response.status == 403) {
    throw messages.MESSAGE_PERMISSION_DENIED
  } else if (response.status == 404) {
    throw messages.MESSAGE_NOT_FOUND_ERROR
  } else if (response.status == 422) {
    throw messages.MESSAGE_UNPROCESSABLE_ENTITY
  } else if (response.status == 504) {
    throw messages.MESSAGE_TIMEOUT_ERROR
  } else if (response.status == 400) {
    throw messages.MESSAGE_BAD_REQUEST_ERROR
  } else if (response.status != 200) {
    throw messages.MESSAGE_UNEXPECTED_ERROR
  } else {
    return response
  }
}

export default {
  get,
  messages,

  checkCredentials: ({ email, password }) => {
    return post(config.apiLoginUrl, { email, password }).then(responseHandler)
  },

  logout: () => {
    return post(config.apiLogoutUrl).then(responseHandler)
  },

  updateExportPlan: (data) => {
    return post(config.apiUpdateExportPlanUrl, data).then(responseHandler)
  },

  createExportPlan: (data) => {
    return post(config.apiCreateExportPlanUrl, data).then((response) =>
      responseHandler(response).json()
    )
  },

  deleteExportPlan: (data) => {
    return post(config.apiDeleteExportPlanUrl, data).then((response) =>
      responseHandler(response).json()
    )
  },

  getCountries: () => {
    return get(config.apiCountriesUrl, {}).then((response) =>
      responseHandler(response).json()
    )
  },

  getSuggestedCountries: (hs_code) => {
    return get(config.apiSuggestedCountriesUrl, { hs_code }).then((response) =>
      responseHandler(response).json()
    )
  },

  getSocietyByCountryData: (countries) => {
    return get(config.societyByCountryUrl, {
      countries: countries.map((obj) => obj.country_name),
    }).then((response) => responseHandler(response).json())
  },

  getComTradeData: (countries, commodity_code) => {
    return get(config.apiComTradeDataUrl, {
      countries: countries.map((obj) => obj.country_iso2_code),
      commodity_code: commodity_code,
    }).then((response) => responseHandler(response).json())
  },

  getCountryData: (countries, fields) => {
    return get(config.apiCountryDataUrl, {
      countries: countries.map((obj) => obj.country_iso2_code),
      fields: fields,
    }).then((response) => responseHandler(response).json())
  },

  getCountryAgeGroupData: (data) => {
    return post(config.apiTargetAgeGroups, data).then((response) =>
      responseHandler(response).json()
    )
  },

  getMarketingCountryData: (data) => {
    return get(config.marketingCountryData, data).then((response) =>
      responseHandler(response).json()
    )
  },

  lookupProduct: ({ proddesc }) => {
    return post(config.apiLookupProductUrl, { proddesc }).then((response) =>
      responseHandler(response).json()
    )
  },

  lookupProductRefine: ({ txId, interactionId, values }) => {
    return post(config.apiLookupProductUrl, {
      tx_id: txId,
      interaction_id: interactionId,
      values: values,
    }).then((response) => responseHandler(response).json())
  },

  lookupProductSchedule: ({ hsCode }) => {
    return get(config.apiLookupProductScheduleUrl, {
      hs_code: hsCode,
    }).then((response) => responseHandler(response).json())
  },

  companiesHouseApi: (parameters) => {
    return get(config.apiCompaniesHouseUrl, parameters).then((response) =>
      responseHandler(response).json()
    )
  },

  getLessonComplete: (endpoint) => {
    return get(endpoint).then(responseHandler)
  },

  setLessonComplete: (endpoint) => {
    return post(endpoint).then(responseHandler)
  },

  setLessonIncomplete: (endpoint) => {
    return httpDelete(endpoint).then(responseHandler)
  },

  createAdaptTarketMarketDocumentList: (data) => {
    return post(
      config.apiTargetMarketDocumentsCreateUrl,
      data
    ).then((response) => responseHandler(response).json())
  },

  deleteAdaptTarketMarketDocumentList: (pk) => {
    return httpDelete(config.apiTargetMarketDocumentsDeleteUrl, {
      pk: pk,
    }).then(responseHandler)
  },

  updateAdaptTarketMarketDocumentList: (data) => {
    return post(
      config.apiTargetMarketDocumentsUpdateUrl,
      data
    ).then((response) => responseHandler(response).json())
  },

  apiModelObjectManage: (data, method) => {
    return greatApi(
      config.apiModelObjectManageUrl,
      data,
      method
    ).then((response) => responseHandler(response).json())
  },

  createUser: ({ email, password, phoneNumber, next }) => {
    return post(
      config.apiSignupUrl,
      { email, password, mobile_phone_number:phoneNumber, next }
    ).then((response) => responseHandler(response))
  },

  checkVerificationCode: ({ uidb64, token, code }) => {
    return post(config.verifyCodeUrl, { uidb64, token, code }).then(responseHandler)
  },

  updateCompany: ({
    company_name,
    expertise_industries,
    expertise_countries,
    first_name,
    last_name,
  }) => {
    const data = {
      company_name,
      expertise_industries,
      expertise_countries,
      first_name,
      last_name,
    }
    return post(config.apiUpdateCompanyUrl, data).then(responseHandler)
  },

  updateCalculateCostAndPricing: (data) =>
    post(config.updateCalculateCostAndPricing, data).then((response) =>
      responseHandler(response).json()
    ),

  updateUserProfileSegment: (segment) => {
    return post(config.apiUserProfileUpdateUrl, {
      segment: segment,
    }).then((response) => responseHandler(response).json())
  },

  getUserQuestionnaire: () => {
    return get(config.apiUserQuestionnaireUrl).then((response) =>
      responseHandler(response).json()
    )
  },

  setUserQuestionnaireAnswer: (questionId, answer) => {
    return post(config.apiUserQuestionnaireUrl, {
      questionId,
      answer,
    }).then((response) => responseHandler(response).json())
  },

  getUserData: (name) => {
    const url = config.apiUserDataUrl.replace('-name-', name)
    return get(url).then((response) => responseHandler(response).json())
  },

  setUserData: (name, data) => {
    const url = config.apiUserDataUrl.replace('-name-', name)
    return post(url, {
      data,
    }).then((response) => responseHandler(response).json())
  },

  reloadPage: () => window.location.reload(),
}
