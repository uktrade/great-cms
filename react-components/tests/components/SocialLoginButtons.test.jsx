import React from 'react'
import { render } from '@testing-library/react'

import SocialLoginButtons from '@src/components/SocialLoginButtons'

test('SocialLoginButtons should render', () => {
  // What a test!
  const linkedinUrl = 'http://www.example.com/linkedInUrl/'
  const googleUrl = 'http://www.example.com/google/'

  const { container } = render(
    <SocialLoginButtons
      linkedinUrl={linkedinUrl}
      googleUrl={googleUrl}
      action="Continue"
    />
  )

  expect(
    container
      .querySelector('[title="Sign up with Linkedin"]')
      .getAttribute('href')
  ).toEqual(linkedinUrl)
  expect(
    container
      .querySelector('[title="Sign up with Google"]')
      .getAttribute('href')
  ).toEqual(googleUrl)
})
