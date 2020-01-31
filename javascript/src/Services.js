const MESSAGE_ACCOUNT_ALREADY_EXISTS = 'Email already registered'
const MESSAGE_UNEXPECTED_ERROR = 'Unexpected Error'
const MESSAGE_INCORRECT_CREDENTIALS = 'Incorrect username or password'


const post = function({url, csrfToken, data}) {
  return fetch(url, {
    method: 'post',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(data),
  })
}


const createUser = function({url, csrfToken, username, password}) {
  const data = {username, password}
  return post({url, csrfToken, data}).then(response => {
    if (response.status == 400) {
      throw MESSAGE_ACCOUNT_ALREADY_EXISTS
    } else if (response.status != 200) {
      throw MESSAGE_UNEXPECTED_ERROR
    }
  })
}


const checkCredentials = function({url, csrfToken, username, password}) {
  const data = {username, password}
  return post({url, csrfToken, data}).then(response => {
    if (response.status == 400) {
      throw MESSAGE_INCORRECT_CREDENTIALS
    } else if (response.status != 200) {
      throw MESSAGE_UNEXPECTED_ERROR
    }
  })
}


export default {
  createUser,
  checkCredentials,
  messages: {
    MESSAGE_ACCOUNT_ALREADY_EXISTS,
    MESSAGE_UNEXPECTED_ERROR,
    MESSAGE_INCORRECT_CREDENTIALS,
  }
}