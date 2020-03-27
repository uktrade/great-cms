import Enzyme from 'enzyme'
import fetchMock from 'fetch-mock'

import Services from '@src/Services'

beforeEach(() => {
  fetchMock.reset()
  jest.useFakeTimers()
  Services.setConfig({
    apiSignupUrl: 'http://www.example.com/signup/',
    apiLoginUrl: 'http://www.example.com/login/',
    csrfToken: '123',
    linkedInUrl: 'http://www.example.com/oauth2/linkedin/',
    googleUrl: 'http://www.example.com/oauth2/google/',
    termsUrl: 'https://www.great.gov.uk/terms-and-conditions/',
    enrolCompanyUrl: 'https://www.great.gov.uk/enrol/',
  })
})

afterEach(() => {
  jest.useRealTimers()
  Services.setConfig({})
})

test('checkCredentials passes params', done => {
  // given the form submission will result in success.getDOMNodeful login
  fetchMock.post(Services.config.apiLoginUrl, 200)

  Services.checkCredentials({email: 'example', password: 'password'})

  fetchMock.flush().then(() => {
    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(Services.config.apiLoginUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
       'Accept': 'application/json',
       'Content-Type': 'application/json',
       'X-CSRFToken': Services.config.csrfToken,
       'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"email":"example","password":"password"}',
    })
    done()
  })
})

test('createUser passes params', done => {
  // given the form submission will result in success.getDOMNodeful login
  fetchMock.post(Services.config.apiSignupUrl, 200)

  Services.createUser({email: 'example', password: 'password'})

  fetchMock.flush().then(() => {
    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(Services.config.apiSignupUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
       'Accept': 'application/json',
       'Content-Type': 'application/json',
       'X-CSRFToken': Services.config.csrfToken,
       'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"email":"example","password":"password"}',
    })
    done()
  })
})
