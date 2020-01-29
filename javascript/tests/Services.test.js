import Enzyme from 'enzyme'
import fetchMock from 'fetch-mock'

import Services from '../src/Services'


const formUrl = 'http://www.example.com/create-user/'
const csrfToken = '123'

beforeEach(() => {
  fetchMock.reset()
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

test('checkCredentials passes params', done => {
  // given the form submission will result in success.getDOMNodeful login
  fetchMock.post(formUrl, 200)

  Services.checkCredentials({url: formUrl, csrfToken: csrfToken, username: 'example', password: 'password'})

  fetchMock.flush().then(() => {
    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(formUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
       'Accept': 'application/json',
       'Content-Type': 'application/json',
       'X-CSRFToken': '123',
       'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"username":"example","password":"password"}',
    })
    done()
  })
})

test('createUser passes params', done => {
  // given the form submission will result in success.getDOMNodeful login
  fetchMock.post(formUrl, 200)

  Services.createUser({url: formUrl, csrfToken: csrfToken, username: 'example', password: 'password'})

  fetchMock.flush().then(() => {
    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(formUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
       'Accept': 'application/json',
       'Content-Type': 'application/json',
       'X-CSRFToken': '123',
       'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"username":"example","password":"password"}',
    })
    done()
  })
})
