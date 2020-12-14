import React from 'react'

import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'
import { ObjectivesList } from '@src/components/ObjectivesList'
import Services from '@src/Services'

const props = {
  objectives: [
    {
      description: 'Some text',
      owner: 'Jane Doe',
      planned_reviews: 'Lorem ipsum',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      isLoading: false,
      showSavedMessage: false,
      errors: {},
    },
    {
      description: 'Some text',
      owner: 'Jane Doe',
      planned_reviews: 'Lorem ipsum',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 2,
      isLoading: false,
      showSavedMessage: false,
      errors: {},
    },
    {
      description: '',
      owner: '',
      planned_reviews: 'Lorem ipsum',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 3,
      isLoading: false,
      showSavedMessage: false,
      errors: {},
    },
  ],
  exportPlanID: 10,
}

const setup = ({ exportPlanID, objectives }) => {
  const component = render(
    <ObjectivesList exportPlanID={exportPlanID} objectives={objectives} />
  )

  return {
    ...component,
  }
}

beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
  cleanup()
})

describe('ObjectivesList', () => {
  it('Should have 3 Objectives', () => {
    const { getByLabelText } = setup({ ...props })
    getByLabelText('Objective 1')
    getByLabelText('Objective 2')
    getByLabelText('Objective 3')
  })

  it('should update an objective', async () => {
    Services.updateObjective = jest.fn(() => Promise.resolve())
    const { container } = setup({ ...props })

    const textarea = container.querySelectorAll('textarea')[0]
    fireEvent.change(textarea, {
      target: { value: 'new plan' },
    })

    await waitFor(() => {
      expect(Services.updateObjective).toHaveBeenCalledTimes(1)
      expect(Services.updateObjective).toHaveBeenLastCalledWith({
        description: 'new plan',
        owner: 'Jane Doe',
        planned_reviews: 'Lorem ipsum',
        start_date: '',
        end_date: '',
        companyexportplan: 1,
        pk: 1,
        isLoading: false,
        showSavedMessage: false,
        errors: {},
      })
      expect(textarea.value).toEqual('new plan')
    })
  })

  it('should add an objective', async () => {
    Services.createObjective = jest.fn(() =>
      Promise.resolve({
        json: () =>
          Promise.resolve({
            companyexportplan: 3,
            description: '',
            end_date: '2020-12-11',
            owner: '',
            pk: 53,
            planned_reviews: '',
            start_date: '2020-12-11',
          }),
      })
    )

    const { getByText, queryByLabelText } = setup({ ...props })
    fireEvent.click(getByText('Add goal 4 of 5'))

    expect(queryByLabelText('Objective 4')).not.toBeInTheDocument()
    await waitFor(() => {
      expect(Services.createObjective).toHaveBeenCalledTimes(1)
      queryByLabelText('Objective 4')
      getByText('Add goal 5 of 5')
    })
  })

  it('Should delete objective', async () => {
    Services.deleteObjective = jest.fn(() => Promise.resolve())
    const { container, queryByLabelText } = setup({ ...props })
    const button = container.querySelectorAll('.button--delete')[2]

    fireEvent.click(button)
    queryByLabelText('Objective 3')
    await waitFor(() => {
      expect(Services.deleteObjective).toHaveBeenCalledTimes(1)
      expect(Services.deleteObjective).toHaveBeenCalledWith(3)
      expect(queryByLabelText('Objective 3')).not.toBeInTheDocument()
    })
  })
})
