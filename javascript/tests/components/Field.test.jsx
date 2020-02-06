import React from 'react'

import { shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import Field from '../../src/components/Field'

Enzyme.configure({ adapter: new Adapter() })


beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})


test('Field should use props', () => {
  const component = shallow(
    <Field 
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
    <div className="form-group">
      <input
        type="text"
        placeholder="some placeholder"
        name="some-name"
        className="form-control"
        value="some value"
        disabled={true}
        autoFocus={true}
      />
    </div>
  )).toEqual(true)
})


test('Field should handle defaul props', () => {
  const component = shallow(
    <Field 
      type='text'
      placeholder='some placeholder'
      name='some-name'
      value='some value'
      handleChange={() => {}}
    />
  )

  expect(component.matchesElement(
    <div className="form-group">
      <input
        type="text"
        placeholder="some placeholder"
        name="some-name"
        className="form-control"
        value="some value"
        disabled={false}
        autoFocus={false}
      />
    </div>
  )).toEqual(true)
})
