import React from 'react'

import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetchMock from 'fetch-mock'

import { Objective } from '@src/components/ObjectivesList/Objective'
import Services from '@src/Services'
import ErrorList from '@src/components/ErrorList'

Enzyme.configure({ adapter: new Adapter() })

const dummyFunction = () => {}

const mockObjectiveData = {
  description: '',
  owner: '',
  planned_reviews: '',
  start_month: '',
  start_year: '',
  end_month: '',
  end_year: '',
  companyexportplan: 1,
  pk: 1,
}

beforeEach(() => {
  jest.useFakeTimers()
  fetchMock.reset()

  Services.setConfig({
    apiObjectivesCreateUrl:
      'http://www.example.com/export-plan/api/objectives/create/',
    apiObjectivesDeleteUrl:
      'http://www.example.com/export-plan/api/objectives/delete/',
    apiObjectivesUpdateUrl:
      'http://www.example.com/export-plan/api/objectives/update/',
  })
})

afterEach(() => {
  jest.useRealTimers()
})

describe('Objective', () => {
  test('should show ErrorList when there are errors', () => {
    const dummyObjective = {
      ...mockObjectiveData,
      errors: { __all__: ['Unexpected error', 'Request timed out'] },
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
        deleteObjective={dummyFunction}
      />
    )

    expect(
      wrapper.containsMatchingElement(
        <ErrorList errors={['Unexpected error', 'Request timed out']} />
      )
    ).toEqual(true)
  })

  test('should not show ErrorList when there are no errors', () => {
    const dummyObjective = {
      ...mockObjectiveData,
      errors: { __all__: [] },
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
        deleteObjective={dummyFunction}
      />
    )

    expect(wrapper.exists('errorlist')).toEqual(false)
  })

  test('should call function on change', () => {
    const mockFunction = jest.fn()

    const dummyObjective = {
      ...mockObjectiveData,
      start_year: 2021, start_month: 4, end_month: 5, end_year: 2021,
      showSavedMessage: false,
      isLoading: false,
      errors: { __all__: [] },
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
        deleteObjective={dummyFunction}
      />
    )

    const input = wrapper.find('textarea[name="description"]')

    const dummyEvent = {
      target: { name: 'description', value: 'Lorem ipsum' },
    }

    input.simulate('change', dummyEvent)

    expect(mockFunction).toHaveBeenCalledWith({
      ...dummyObjective,
      description: 'Lorem ipsum',
    })
  })


  test('should not call function on change if start date precede end date', () => {
    const mockFunction = jest.fn()

    const dummyObjective = {
      ...mockObjectiveData,
      start_year: 2021, start_month: 5, end_month: 4, end_year: 2021,
      showSavedMessage: false,
      isLoading: false,
      errors: { __all__: [] },
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
        deleteObjective={dummyFunction}
      />
    )

    const input = wrapper.find('textarea[name="description"]')

    const dummyEvent = {
      target: { name: 'description', value: 'Lorem ipsum' },
    }

    input.simulate('change', dummyEvent)

    expect(mockFunction).toHaveBeenCalledWith({
      ...dummyObjective,
      description: 'Lorem ipsum',
    })
  })

  test('should call function on delete', () => {
    const mockFunction = jest.fn()

    const dummyObjective = {
      ...mockObjectiveData,
      pk: 234,
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
        deleteObjective={mockFunction}
      />
    )

    const input = wrapper.find('.button--delete')

    input.simulate('click', {})

    expect(mockFunction).toHaveBeenCalledWith(234)
  })
})
