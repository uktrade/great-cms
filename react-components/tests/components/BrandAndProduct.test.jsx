import React from 'react'

import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetchMock from 'fetch-mock'
import { fakeSchedulers } from 'rxjs-marbles/jest'

import { BrandAndProductForm } from '@src/components/BrandAndProduct'
import FieldWithExample from '@src/components/Fields/FieldWithExample'
import Services from '@src/Services'

Enzyme.configure({ adapter: new Adapter() })

let wrapper;

const dummyFieldOne = {
  name: 'field_one',
  label: 'Field one',
  tooltip: 'This is a tooltip',
  description: 'This is a description',
  example: '<p>An example of the required text</p>',
  placeholder: 'Add some text',
  currency: 'GBP',
  tag: 'text'
}

const formData = {
  field_one: 'Some value'
}

beforeEach(() => {
  jest.useFakeTimers()
  fetchMock.reset()

  wrapper = Enzyme.mount(
    <BrandAndProductForm
      formFields={[dummyFieldOne]}
      formData={formData}
    />
  )

  Services.setConfig({
    apiUpdateExportPlanUrl: 'http://www.example.com/update-export-plan/',
  })

})

afterEach(() => {
  jest.useRealTimers()
})

describe('BrandAndProductForm', () => {
  test('should generate form fields from props and prepopulate', () => {

    expect(wrapper.containsMatchingElement(
      <FieldWithExample
        tooltip={dummyFieldOne.tooltip}
        label={dummyFieldOne.label}
        key={dummyFieldOne.name}
        name={dummyFieldOne.name}
        value={formData.field_one}
        description={dummyFieldOne.description}
        placeholder={dummyFieldOne.placeholder}
        currency={dummyFieldOne.currency}
        tag={dummyFieldOne.tag}
        example={dummyFieldOne.example}
      />
    )).toEqual(true)
  })

  test('should update formData on change', () => {

    expect(wrapper.state('formData')).toBe(formData)
    const input = wrapper.find('textarea')

    // change value of form field
    const dummyEvent = {
      target: {name: 'field_one', value: 'Lorem ipsum'}
    }

    input.simulate('change', dummyEvent)

    // check formData state has changed
    expect(wrapper.state('formData')).toStrictEqual({
      field_one: 'Lorem ipsum'
    })

  })

  test('should debounce input', fakeSchedulers(advance => {

    fetchMock.post(Services.config.apiUpdateExportPlanUrl, 200)

    const input = wrapper.find('textarea')

    expect(wrapper.state('isLoading')).toBe(false)

    // change value of form field
    const dummyEvent = {
      target: {name: 'field_one', value: 'Lorem ipsum'}
    }

    input.simulate('change', dummyEvent)

    // wait for debounce
    advance(1000 * 2)

    expect(wrapper.state('isLoading')).toBe(true)

  }))

  test('should show saved message after debounced input', fakeSchedulers(advance => {

    fetchMock.post(Services.config.apiUpdateExportPlanUrl, 200)

    expect(wrapper.state('showSavedMessage')).toBe(false)

    wrapper.instance().handleUpdateSuccess()

    // wait for debounce
    advance(1000 * 2)
    expect(wrapper.state('showSavedMessage')).toBe(true)

  }))

  test('should hide saved message after 2 secs', fakeSchedulers(advance => {

    fetchMock.post(Services.config.apiUpdateExportPlanUrl, 200)

    expect(wrapper.state('showSavedMessage')).toBe(false)

    wrapper.instance().handleUpdateSuccess()

    advance(1000 * 2)
    expect(wrapper.state('showSavedMessage')).toBe(true)

  }))

})
