import React from 'react'

import { shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import SocialLoginButtons from '@src/components/SocialLoginButtons'
import Services from '@src/Services'


Enzyme.configure({ adapter: new Adapter() })


const linkedInUrl = 'http://www.example.com/linkedInUrl/'
const googleUrl = 'http://www.example.com/google/'


beforeEach(() => {
  Services.setConfig({linkedInUrl, googleUrl})
  jest.useFakeTimers()
})

afterEach(() => {
  Services.setConfig({})
  jest.useRealTimers()
})


test('SocialLoginButtons should render', () => {
  const component = shallow(
    <SocialLoginButtons
      type='text'
      placeholder='some placeholder'
      name='some-name'
      value='some value'
      handleChange={() => {}}
      disabled={true}
      autofocus={true}
    />
  )

  expect(component.matchesElement(
    <div>
      <a href={linkedInUrl} className="g-button m-t-0 m-b-xs">
        <img />
        <span>Continue with LinkedIn</span>
      </a>
      <a href={googleUrl} className="g-button m-t-0 m-b-xs">
        <img />
        <span >Continue with Google</span>
      </a>
    </div>
  )).toEqual(true)
})
