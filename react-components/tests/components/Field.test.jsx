import React from 'react'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import Field, { TextInput, RadioInput } from '@src/components/Fields/Field'
import ErrorList from '@src/components/ErrorList'

Enzyme.configure({ adapter: new Adapter() })

beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

test('Field should use props', () => {
  const errors = ['some error']
  const component = Enzyme.shallow(
    <Field
      type="text"
      placeholder="some placeholder"
      name="some-name"
      value="some value"
      handleChange={() => {}}
      disabled
      autofocus
      errors={errors}
    />
  )

  expect(
    component.matchesElement(
      <div>
        <ErrorList errors={errors} />
        <TextInput
          id="id_some-name"
          value="some value"
          name="some-name"
          placeholder="some placeholder"
          type="text"
          autofocus
          disabled
        />
      </div>
    )
  ).toEqual(true)
})

test('Field should render radio', () => {
  const errors = []
  const options = [
    { value: 'foo', label: 'Foo', disabled: true },
    { value: 'bar', label: 'Bar', disabled: false },
  ]
  const component = Enzyme.shallow(
    <Field
      type="radio"
      placeholder="some placeholder"
      name="some-name"
      options={options}
      value="bar"
      handleChange={() => {}}
      errors={errors}
    />
  )
  expect(
    component.containsMatchingElement(
      <RadioInput
        id="id_some-name"
        type="radio"
        placeholder="some placeholder"
        name="some-name"
        options={options}
        value="bar"
        errors={errors}
        autofocus={false}
        disabled={false}
      />
    )
  ).toEqual(true)
})

test('Field should handle default props', () => {
  const errors = []
  const component = Enzyme.shallow(
    <Field
      type="text"
      placeholder="some placeholder"
      name="some-name"
      value="some value"
      handleChange={() => {}}
      errors={errors}
    />
  )

  expect(
    component.containsMatchingElement(
      <div>
        <ErrorList errors={errors} />
        <TextInput
          id="id_some-name"
          autofocus={false}
          disabled={false}
          errors={errors}
          placeholder="some placeholder"
          type="text"
          name="some-name"
          value="some value"
        />
      </div>
    )
  ).toEqual(true)
})
