import React from 'react'
import { render, waitFor } from '@testing-library/react'
import Services from '@src/Services'

import { Login } from '@src/components/Login'


const defaultProps = {
  email: 'email',
  password: 'password',
  nextUrl: '/thing/',
  linkedinLoginUrl: 'http://www.example.com/oauth2/linkedin',
  googleLoginUrl: 'http://www.example.com/oauth2/google',
}

describe('LoginModal', () => {
  const { assign } = window.location

  beforeEach(() => {
    delete window.location
    window.location = { assign: jest.fn() }
  })

  afterEach(() => {
    window.location.assign = assign
  })

  it('shows an error when credentials are incorrect', async () => {
    // given the credentials are incorrect
    Services.checkCredentials = jest.fn().mockRejectedValue({
      email: ['This field is required'],
    })

    const { container } = render(<Login {...defaultProps} />)

    // when the form is submitted
    container.querySelector('form').submit()

    await waitFor(() => {
      expect(container.querySelector('.govuk-error-message').textContent).toEqual(
        'This field is required'
      )
    })
  })

  it('redirects to next url when credentials are correct and user verified', async () => {
    // given the credentials are correct and user is verified

    Services.checkCredentials = jest.fn().mockResolvedValue({
      json: async () => ({})
    })
    const { container } = render(<Login {...defaultProps} />)

    container.querySelector('form').submit()
    await waitFor(() => {
      expect(window.location.assign).toHaveBeenCalledWith(defaultProps.nextUrl)
    })
  })

  it('redirects to signup url with correct query string when credentials are correct but user not verified', async () => {
    // given the credentials are correct but user unverified
    Services.setConfig({
      signupUrl: '/signup/'
    })

    const token = '1234'
    const uidb64 = 'ABC'

    Services.checkCredentials = jest.fn().mockResolvedValue({
      json: async () => ({ token, uidb64 })
    })

    const { container } = render(<Login {...defaultProps} />)
    container.querySelector('form').submit()

    await waitFor(() => {
      expect(window.location.assign).toHaveBeenCalledWith('/signup/?uidb64=ABC&token=1234')
    })
  })

  it('redirects to signup url with next parameter when credentials are correct but user not verified', async () => {
    // given the credentials are correct but user unverified and there is already a next query parameter in the URL

    const nextQueryString = '?next=/dashboard/'
    window.location.search = nextQueryString

    Services.setConfig({
      signupUrl: `/signup/${nextQueryString}`
    })

    const token = '1234'
    const uidb64 = 'ABC'

    Services.checkCredentials = jest.fn().mockResolvedValue({
      json: async () => ({ token, uidb64 })
    })

    const { container } = render(<Login {...defaultProps} />)
    container.querySelector('form').submit()

    await waitFor(() => {
      expect(window.location.assign).toHaveBeenCalledWith('/signup/?next=/dashboard/&uidb64=ABC&token=1234')
    })
  })
})
