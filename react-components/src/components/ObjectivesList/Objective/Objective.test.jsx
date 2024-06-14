import React from 'react'
import { act, fireEvent, render } from '@testing-library/react'
import fetchMock from 'fetch-mock'
import Services from '@src/Services'

import { Objective } from '@src/components/ObjectivesList/Objective'

const dummyFunction = () => {}

const mockObjectiveData = {
  description: '',
  owner: '',
  planned_reviews: '',
  end_month: '',
  end_year: '',
  companyexportplan: 1,
  pk: 1,
}

beforeEach(() => {
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

describe('Objective', () => {
  it('should show ErrorList when there are errors', () => {
    const dummyObjective = {
      ...mockObjectiveData,
      errors: { __all__: ['Unexpected error', 'Request timed out'] },
    }

    const { container } = render(
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

    const errorItems = container.querySelectorAll('.govuk-error-message')

    expect(errorItems).toHaveLength(2)
    expect(errorItems[0].textContent).toEqual('Unexpected error')
    expect(errorItems[1].textContent).toEqual('Request timed out')
  })

  it('should not show ErrorList when there are no errors', () => {
    const dummyObjective = {
      ...mockObjectiveData,
      errors: { __all__: [] },
    }

    const { container } = render(
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

    expect(container.querySelector('.errorlist')).toBeNull()
  })

  it('should call function on change', () => {
    const mockFunction = jest.fn()

    const dummyObjective = {
      ...mockObjectiveData,
      showSavedMessage: false,
      isLoading: false,
      errors: { __all__: [] },
    }

    const { container } = render(
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

    const input = container.querySelector('textarea[name="description"]')

    fireEvent.change(input, {
      target: { name: 'description', value: 'Lorem ipsum' },
    })

    expect(mockFunction).toHaveBeenCalledWith({
      ...dummyObjective,
      description: 'Lorem ipsum',
    })
  })

  it('should call function on delete', () => {
    const mockFunction = jest.fn()

    const dummyObjective = {
      ...mockObjectiveData,
      pk: 234,
    }

    const { container } = render(
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

    act(() => {
      container.querySelector('.delete-button').click()
    })

    expect(mockFunction).toHaveBeenCalledWith(234)
  })
})
