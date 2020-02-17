import Enzyme from 'enzyme'
import fetchMock from 'fetch-mock'

import Services from '@src/Services'

beforeEach(() => {
  fetchMock.reset()
  jest.useFakeTimers()
  Services.setConfig({
    signupUrl: 'http://www.example.com/signup/',
    loginUrl: 'http://www.example.com/login/',
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
  fetchMock.post(Services.config.loginUrl, 200)

  Services.checkCredentials({username: 'example', password: 'password'})

  fetchMock.flush().then(() => {
    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(Services.config.loginUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
       'Accept': 'application/json',
       'Content-Type': 'application/json',
       'X-CSRFToken': Services.config.csrfToken,
       'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"username":"example","password":"password"}',
    })
    done()
  })
})

test('createUser passes params', done => {
  // given the form submission will result in success.getDOMNodeful login
  fetchMock.post(Services.config.signupUrl, 200)

  Services.createUser({username: 'example', password: 'password'})

  fetchMock.flush().then(() => {
    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(Services.config.signupUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
       'Accept': 'application/json',
       'Content-Type': 'application/json',
       'X-CSRFToken': Services.config.csrfToken,
       'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"username":"example","password":"password"}',
    })
    done()
  })
})

test('enrolCompany passes params', done => {
  // given the form submission will result in success.getDOMNodeful login
  fetchMock.post(Services.config.enrolCompanyUrl, 200)
  const data = {
    company_name: 'a',
    expertise_industries: 'b',
    expertise_countries: 'c',
    first_name: 'd',
    last_name: 'e',
  }

  Services.enrolCompany(data)

  fetchMock.flush().then(() => {
    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(Services.config.enrolCompanyUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
       'Accept': 'application/json',
       'Content-Type': 'application/json',
       'X-CSRFToken': Services.config.csrfToken,
       'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(data)
    })
    done()
  })
})

