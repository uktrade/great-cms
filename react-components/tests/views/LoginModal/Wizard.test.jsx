import React from 'react'
import { render, waitFor } from '@testing-library/react'
import Services from '@src/Services'

import { Login } from '@src/components/Login'

jest.mock('@src/Services')

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

    Services.setConfig({
      apiLoginUrl: 'http://www.example.com/login/',
      csrfToken: '123',
      linkedInUrl: 'http://www.example.com/oauth2/linkedin',
      googleUrl: 'http://www.example.com/oauth2/google',
      dashboardUrl: '/dashboard/',
    })
  })

  afterEach(() => {
    window.location.assign = assign

    Services.setConfig({})
  })

  it('shows an error when credentials are incorrect', async () => {
    // given the credentials are incorrect
    Services.checkCredentials.mockRejectedValue({
      email: ['This field is required'],
    })

    const { container } = render(<Login {...defaultProps} />)

    // when the form is submitted
    container.querySelector('form').submit()

    await waitFor(() => {
      expect(container.querySelector('.error-message').textContent).toEqual(
        'This field is required'
      )
    })
  })

  it('redirects to next url when credentials are correct', async () => {
    // given the credentials are correct
    Services.checkCredentials.mockResolvedValue()
    const { container } = render(<Login {...defaultProps} />)

    container.querySelector('form').submit()

    await waitFor(() => {
      expect(window.location.assign).toHaveBeenCalled()
    })
  })
})
