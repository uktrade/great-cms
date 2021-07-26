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
      start_month: '',
      start_year: '',
      end_month: '',
      end_year: '',
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
      start_month: '',
      start_year: '',
      end_month: '',
      end_year: '',
      companyexportplan: 1,
      pk: 2,
      isLoading: false,
      showSavedMessage: false,
      errors: {},
    },
    {
      description: 'Some text',
      owner: 'Jane Doe',
      planned_reviews: 'Lorem ipsum',
      start_month: '',
      start_year: '',
      end_month: '',
      end_year: '',
      companyexportplan: 1,
      pk: 3,
    },
  ],
  exportPlanID: 10,
  model_name: 'objectives',
}

const setup = ({ exportPlanID, objectives, model_name = 'objectives' }) => {
  const component = render(
    <ObjectivesList
      exportPlanID={exportPlanID}
      objectives={objectives}
      model_name={model_name}
    />
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
  Services.apiModelObjectManage.mockClear()
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
    Services.apiModelObjectManage = jest.fn(() => Promise.resolve())
    const { container } = setup({ ...props })

    const textarea = container.querySelectorAll('textarea')[0]
    fireEvent.change(textarea, {
      target: { value: 'new plan' },
    })

    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenLastCalledWith(
        {
          description: 'new plan',
          owner: 'Jane Doe',
          planned_reviews: 'Lorem ipsum',
          start_month: '',
          start_year: '',
          end_month: '',
          end_year: '',
          companyexportplan: 1,
          pk: 1,
          isLoading: false,
          showSavedMessage: false,
          errors: {},
          model_name: 'objectives',
        },
        'PATCH'
      )
      expect(textarea.value).toEqual('new plan')
    })
  })

  it('Should delete objective', async () => {
    Services.apiModelObjectManage = jest.fn(() => Promise.resolve())
    const { container, queryByLabelText } = setup({
      ...props,
      objectives: [
        {
          description: 'Some text',
          owner: 'Jane Doe',
          planned_reviews: 'Lorem ipsum',
          start_month: '',
          start_year: '',
          end_month: '',
          end_year: '',
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
          start_month: '',
          start_year: '',
          end_month: '',
          end_year: '',
          companyexportplan: 1,
          pk: 2,
          isLoading: false,
          showSavedMessage: false,
          errors: {},
        },
        {
          description: '',
          owner: '',
          planned_reviews: '',
          start_month: '',
          start_year: '',
          end_month: '',
          end_year: '',
          companyexportplan: 1,
          pk: 3,
        },
      ],
    })
    const button = container.querySelectorAll('.button--delete')[2]

    fireEvent.click(button)
    queryByLabelText('Objective 3')
    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        {
          pk: 3,
          model_name: 'objectives',
        },
        'DELETE'
      )
      expect(queryByLabelText('Objective 3')).not.toBeInTheDocument()
    })
  })

  describe('Add button', () => {
    describe('should add an objective', () => {
      Services.apiModelObjectManage = jest.fn(() =>
        Promise.resolve({
          json: () =>
            Promise.resolve({
              companyexportplan: 3,
              description: '',
              start_month: '12',
              start_year: '2020',
              end_month: '12',
              end_year: '2020',
              owner: '',
              pk: 53,
              planned_reviews: '',
            }),
        })
      )

      // it('uses current date for initial data', async () => {
      //   const { getByText } = setup({
      //     ...props,
      //     objectives: [],
      //   })
      //   fireEvent.click(getByText('Add goal 1 of 5'))

      //   await waitFor(() => {
      //     expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      //     const requestData = Services.apiModelObjectManage.mock.calls[0][0]
      //     expect(requestData.start_month).toBe(7)
      //     expect(requestData.start_year).toBe(2021)
      //     expect(requestData.end_month).toBe(7)
      //     expect(requestData.end_year).toBe(2021)
      //   })
      // })

      it('initial load', async () => {
        const { getByText, queryByLabelText } = setup({
          ...props,
          objectives: [],
        })
        fireEvent.click(getByText('Add goal 1 of 5'))

        expect(queryByLabelText('Objective 1')).not.toBeInTheDocument()
        await waitFor(() => {
          expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
          queryByLabelText('Objective 1')
          getByText('Add goal 2 of 5')
        })
      })

      it('has multiple element', async () => {
        const { getByText, queryByLabelText } = setup({ ...props })
        fireEvent.click(getByText('Add goal 4 of 5'))

        expect(queryByLabelText('Objective 4')).not.toBeInTheDocument()
        await waitFor(() => {
          expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
          queryByLabelText('Objective 4')
          getByText('Add goal 5 of 5')
        })
      })
    })
    it('Should be disabled', async () => {
      const { getByText, queryByLabelText } = setup({
        ...props,
        objectives: [
          {
            companyexportplan: 3,
            description: '',
            start_month: '12',
            start_year: '2020',
            end_month: '12',
            end_year: '2020',
            owner: '',
            pk: 53,
            planned_reviews: '',
          },
        ],
      })

      fireEvent.click(getByText('Add goal 2 of 5'))

      expect(queryByLabelText('Objective 2')).not.toBeInTheDocument()
      await waitFor(() => {
        expect(Services.apiModelObjectManage).not.toHaveBeenCalled()
      })
    })
  })
})
