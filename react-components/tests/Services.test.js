import fetchMock from 'fetch-mock'
import Services from '@src/Services'

describe('Services', () => {
  beforeEach(() => {
    Services.setConfig({
      apiSignupUrl: '/signup/',
      apiLoginUrl: '/login/',
      apiLookupProductUrl: '/lookup/',
      csrfToken: '123',
      linkedInUrl: 'http://www.example.com/oauth2/linkedin/',
      googleUrl: 'http://www.example.com/oauth2/google/',
      termsUrl: 'https://www.great.gov.uk/terms-and-conditions/',
      enrolCompanyUrl: 'https://www.great.gov.uk/enrol/',
      apiUserProfileUpdateUrl: '/user-profile/',
    })
  })

  afterEach(() => {
    fetchMock.reset()
    Services.setConfig({})
  })

  test('checkCredentials passes params', async () => {
    // given the form submission will result in success.getDOMNodeful login
    fetchMock.post(Services.config.apiLoginUrl, 200)

    await Services.checkCredentials({ email: 'example', password: 'password' })

    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(Services.config.apiLoginUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Services.config.csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"email":"example","password":"password"}',
    })
  })

  test('createUser passes params', async () => {
    // given the form submission will result in success.getDOMNodeful login
    fetchMock.post(Services.config.apiSignupUrl, 200)

    await Services.createUser({ email: 'example', password: 'password' })

    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual(Services.config.apiSignupUrl)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Services.config.csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"email":"example","password":"password"}',
    })
  })

  test('lookupProduct passes params', async () => {
    // given the form submission will result in success.getDOMNodeful login
    fetchMock.post(Services.config.apiLookupProductUrl, {})

    await Services.lookupProduct({ proddesc: 'foo' })

    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Services.config.csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"proddesc":"foo"}',
    })
  })

  test('updateUserProfileSegment passes params', async () => {
    // given the form submission will result in success.getDOMNodeful login
    fetchMock.post(Services.config.apiUserProfileUpdateUrl, {})

    await Services.updateUserProfileSegment('foo')

    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': Services.config.csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"segment":"foo"}',
    })
  })
})
