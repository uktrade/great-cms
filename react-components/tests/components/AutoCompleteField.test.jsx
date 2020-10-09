import React from 'react'

import { act } from 'react-dom/test-utils'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import Select from 'react-select'
import AsyncSelect from 'react-select/async'

import AutoCompleteField from '@src/components/AutoCompleteField'
import ErrorList from '@src/components/ErrorList'

Enzyme.configure({ adapter: new Adapter() })

beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

describe('AutoCompleteField', () => {
  test('should show errors', () => {
    const errors = ['some error']
    const component = Enzyme.shallow(
      <AutoCompleteField
        autoFocus
        disabled={false}
        errors={errors}
        handleChange={() => {}}
        options={[{ value: 'foo', label: 'Foo' }]}
        name="example"
        placeholder="Some placeholder"
        value={[{ value: 'foo', label: 'Foo' }]}
      />
    )

    expect(component.containsMatchingElement(<ErrorList errors={errors} />)).toEqual(true)
  })

  test('should handle async lookup', () => {
    const loadOptions = () => Promise.resolve([])

    const component = Enzyme.shallow(
      <AutoCompleteField
        autoFocus
        disabled={false}
        errors={[]}
        handleChange={() => {}}
        loadOptions={loadOptions}
        name="example"
        placeholder="Some placeholder"
        value={[{ value: 'foo', label: 'Foo' }]}
      />
    )

    expect(
      component.containsMatchingElement(
        <AsyncSelect
          autoFocus
          className="great-mvp-autocomplete-field"
          classNamePrefix="great-mvp-autocomplete-field"
          disabled={false}
          id="id_example"
          isClearable
          isMulti
          loadOptions={loadOptions}
          name="example"
          placeholder="Some placeholder"
          value={[{ value: 'foo', label: 'Foo' }]}
        />
      )
    ).toBe(true)
  })

  test('should handle sync lookup', () => {
    const options = [
      { value: 'foo', label: 'Foo' },
      { value: 'bar', label: 'Bar' },
    ]
    const component = Enzyme.shallow(
      <AutoCompleteField
        autoFocus
        disabled={false}
        errors={[]}
        handleChange={() => {}}
        options={options}
        name="example"
        placeholder="Some placeholder"
        value={[{ value: 'foo', label: 'Foo' }]}
      />
    )

    expect(
      component.containsMatchingElement(
        <Select
          autoFocus
          className="great-mvp-autocomplete-field"
          classNamePrefix="great-mvp-autocomplete-field"
          disabled={false}
          id="id_example"
          isClearable
          isMulti
          options={options}
          name="example"
          placeholder="Some placeholder"
          value={[{ value: 'foo', label: 'Foo' }]}
        />
      )
    ).toBe(true)
  })

  test('should handle no label', () => {
    const component = Enzyme.shallow(
      <AutoCompleteField
        autoFocus
        disabled={false}
        errors={[]}
        handleChange={() => {}}
        options={[{ value: 'foo', label: 'Foo' }]}
        name="example"
        placeholder="Some placeholder"
        value={[{ value: 'foo', label: 'Foo' }]}
        label="Some label"
      />
    )

    expect(
      component.containsMatchingElement(
        <label htmlFor="id_example" className="great-mvp-field-label">
          Some label
        </label>
      )
    ).toBe(true)
  })

  test('should handle clearing value', () => {
    const handleChange = jest.fn()
    const component = Enzyme.shallow(
      <AutoCompleteField
        autoFocus
        disabled={false}
        errors={[]}
        handleChange={handleChange}
        options={[{ value: 'foo', label: 'Foo' }]}
        name="example"
        placeholder="Some placeholder"
        value={[{ value: 'foo', label: 'Foo' }]}
      />
    )
    // when the selection is cleared
    act(() => {
      component.find(Select).prop('onChange')(undefined, {})
    })

    // then an empty array is propagated
    expect(handleChange).toHaveBeenCalledWith([])
  })

  test('should handle setting value', () => {
    const options = [
      { value: 'foo', label: 'Foo' },
      { value: 'bar', label: 'Bar' },
    ]
    const handleChange = jest.fn()

    const component = Enzyme.shallow(
      <AutoCompleteField
        autoFocus
        disabled={false}
        errors={[]}
        handleChange={handleChange}
        options={options}
        name="example"
        placeholder="Some placeholder"
        value={[{ value: 'foo', label: 'Foo' }]}
      />
    )
    // when a value is selected
    act(() => {
      component.find(Select).prop('onChange')([{ value: 'bar', label: 'Bar' }], {})
    })

    // then the value is propagated
    expect(handleChange).toHaveBeenCalledWith([{ value: 'bar', label: 'Bar' }])
  })
})
