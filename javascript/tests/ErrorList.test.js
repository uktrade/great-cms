import React from 'react'
import { shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import ErrorList from '../src/ErrorList'


Enzyme.configure({ adapter: new Adapter() })


beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

test('ErrorList displays the message', () => {
  const component = shallow(<ErrorList message='some error' />)

  expect(component.find('li').text()).toEqual('some error')
})
