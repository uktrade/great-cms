import React from 'react'

import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetchMock from 'fetch-mock'

import { Objective } from '@src/components/ObjectivesList/Objective'
import Field from '@src/components/Fields/Field'
import Services from '@src/Services'
import ErrorList from '@src/components/ErrorList'
import { TextArea } from '@src/components/Form/TextArea'
import { Input } from '@src/components/Form/Input'

Enzyme.configure({ adapter: new Adapter() })

const dummyFunction = () => {}


beforeEach(() => {
  jest.useFakeTimers()
  fetchMock.reset()

  Services.setConfig({
    apiObjectivesCreateUrl: 'http://www.example.com/export-plan/api/objectives/create/',
    apiObjectivesDeleteUrl: 'http://www.example.com/export-plan/api/objectives/delete/',
    apiObjectivesUpdateUrl: 'http://www.example.com/export-plan/api/objectives/update/',
  })

})

afterEach(() => {
  jest.useRealTimers()
})

describe('Objective', () => {

  test('should show saved message when objective has been saved', () => {

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      showSavedMessage: true,
      isLoading: false,
    }

    const wrapper = Enzyme.mount(
      <Objective
        key={0}
        id={0}
        isLoading={dummyObjective.isLoading}
        errors={dummyObjective.errors}
        showSavedMessage={dummyObjective.showSavedMessage}
        data={dummyObjective}
        number={1}
        handleChange={dummyFunction}
        deleteObjective={dummyFunction}/>
    )

    expect(wrapper.containsMatchingElement(
      <p id="objective-saved-message">Changes saved.</p>
    )).toEqual(true)

  })

  test('should show ErrorList when there are errors', () => {

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      errors: {__all__: ['Unexpected error', 'Request timed out']}
    }

    const wrapper = Enzyme.mount(
      <Objective
        key={0}
        id={0}
        isLoading={dummyObjective.isLoading}
        errors={dummyObjective.errors}
        showSavedMessage={dummyObjective.showSavedMessage}
        data={dummyObjective}
        number={1}
        handleChange={dummyFunction}
        deleteObjective={dummyFunction}/>
    )

    expect(wrapper.containsMatchingElement(
      <ErrorList errors={['Unexpected error', 'Request timed out']} />
    )).toEqual(true)

  })

  test('should not show ErrorList when there are no errors', () => {

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      errors: {__all__: []}
    }

    const wrapper = Enzyme.mount(
      <Objective
        key={0}
        id={0}
        isLoading={dummyObjective.isLoading}
        errors={dummyObjective.errors}
        showSavedMessage={dummyObjective.showSavedMessage}
        data={dummyObjective}
        number={1}
        handleChange={dummyFunction}
        deleteObjective={dummyFunction}/>
    )

    expect(wrapper.exists('errorlist')).toEqual(false)

  })

  test('should call function on change', () => {

    const mockFunction = jest.fn()

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      showSavedMessage: false,
      isLoading: false,
      errors: {__all__: []}
    }

    const wrapper = Enzyme.mount(
      <Objective
        key={0}
        id={0}
        isLoading={dummyObjective.isLoading}
        errors={dummyObjective.errors}
        showSavedMessage={dummyObjective.showSavedMessage}
        data={dummyObjective}
        number={1}
        handleChange={mockFunction}
        deleteObjective={dummyFunction}/>
    )

    const input = wrapper.find('textarea[name="description"]')

    const dummyEvent = {
      target: {name: 'description', value: 'Lorem ipsum'}
    }

    input.simulate('change', dummyEvent)

    expect(mockFunction).toHaveBeenCalled()

  })

  test('should call function on delete', () => {

    const mockFunction = jest.fn()

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      showSavedMessage: false,
      isLoading: false,
      errors: {__all__: []}
    }

    const wrapper = Enzyme.mount(
      <Objective
        key={0}
        id={0}
        isLoading={dummyObjective.isLoading}
        errors={dummyObjective.errors}
        showSavedMessage={dummyObjective.showSavedMessage}
        data={dummyObjective}
        number={1}
        handleChange={dummyFunction}
        deleteObjective={mockFunction}/>
    )

    const input = wrapper.find('.button--delete')

    input.simulate('click', {})

    expect(mockFunction).toHaveBeenCalled()

  })


})
