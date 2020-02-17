import React from 'react'

import { shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import Field from '../../src/components/Field'
import ErrorList from '../../src/components/ErrorList'


Enzyme.configure({ adapter: new Adapter() })


beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})


test('Field should use props', () => {
  const errors = ['some error']
  const component = shallow(
    <Field 
      type='text'
      placeholder='some placeholder'
      name='some-name'
      value='some value'
      handleChange={() => {}}
      disabled={true}
      autofocus={true}
      errors={errors}
    />
  )

  expect(component.matchesElement(
    <div className="form-group great-mvp-field">
      <ErrorList errors={errors} />
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
  const errors = []
  const component = shallow(
    <Field 
      type='text'
      placeholder='some placeholder'
      name='some-name'
      value='some value'
      handleChange={() => {}}
      errors={errors}
    />
  )

  expect(component.containsMatchingElement(
    <div className="form-group great-mvp-field">
      <ErrorList errors={errors} />
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
