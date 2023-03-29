/* eslint-disable */

const post = (url, data) => {
    return fetch(url, {
        method: 'post',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': iooConfig.csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify(data),
    })
}

const MESSAGE_UNEXPECTED_ERROR = { __all__: ['Unexpected Error'] }
const MESSAGE_PERMISSION_DENIED = { __all__: ['You do not have permission to perform this action'] }
const MESSAGE_NOT_FOUND_ERROR = { __all__: ['Not found'] }
const MESSAGE_TIMEOUT_ERROR = { __all__: ['Request timed out'] }
const MESSAGE_BAD_REQUEST_ERROR = { __all__: ['Bad request'] }
const MESSAGE_UNPROCESSABLE_ENTITY = { __all__: ['Unprocessable entity'] }

const messages = {
  MESSAGE_UNEXPECTED_ERROR,
  MESSAGE_PERMISSION_DENIED,
  MESSAGE_NOT_FOUND_ERROR,
  MESSAGE_TIMEOUT_ERROR,
  MESSAGE_UNPROCESSABLE_ENTITY
}

const responseHandler = (response) => {
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


const createUser = ({ email, password, phoneNumber }) => {
    return post(iooConfig.apiSignupUrl,
        { email, password, mobile_phone_number:phoneNumber }
    ).then((response) => responseHandler(response))
};

const checkCredentials = ({ email, password }) => {
    return post(iooConfig.apiLoginUrl, { email, password }).then(responseHandler)
};

const logout = () => {
    return post(iooConfig.apiLogoutUrl).then(responseHandler)
};

const checkVerificationCode = ({ uidb64, token, code }) => {
    debugger;
    return post(iooConfig.verifyCodeUrl, { uidb64, token, code }).then(responseHandler)
};
