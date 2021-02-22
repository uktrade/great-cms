import React from 'react'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'
import Services from '@src/Services'
import { BusinessRisks } from './BusinessRisks'

const model_name = 'businessrisk'
const props = {
  formFields: [
    {
      companyexportplan: 1,
      contingency_plan: 'Contingency plan note',
      pk: 60,
      risk: 'Risk note',
      risk_impact: 'SEVERE',
      risk_likelihood: 'RARE',
    },
    {
      companyexportplan: 1,
      contingency_plan: 'Contingency plan note',
      pk: 61,
      risk: 'Risk note',
      risk_impact: 'MINOR',
      risk_likelihood: 'LIKELY',
    },
  ],
  formData: {
    contingency_plan_extras: {
      label: 'Contingency plan',
      tooltip: { content: '<p>Contingency plan notes</p>' },
      example: { content: 'Safety when operating abroad [contingency notes]' },
    },
    risk_extras: {
      tooltip: { content: '<p>Risk notes</p>' },
      example: { content: 'Safety when operating abroad [notes]' },
    },
  },
  risk_likelihood_options: [
    { label: 'Rare', value: 'RARE' },
    { label: 'Unlikely', value: 'UNLIKELY' },
    { label: 'Possible', value: 'POSSIBLE' },
    { label: 'Likely', value: 'LIKELY' },
    { label: 'Certain', value: 'CERTAIN' },
  ],
  risk_impact_options: [
    { label: 'Trivial', value: 'TRIVIAL' },
    { label: 'Minor', value: 'MINOR' },
    { label: 'Moderate', value: 'MODERATE' },
    { label: 'Major', value: 'MAJOR' },
    { label: 'Severe', value: 'SEVERE' },
  ],
  companyexportplan: 1,
  model_name,
  lesson: {
    url: '/',
    title: 'Safety when operating abroad',
    category: 'TBD',
    duration: '3 minutes',
  },
}

const setup = ({ ...data }) => {
  const component = render(
    <BusinessRisks {...data}>
      <p>The child component</p>
    </BusinessRisks>
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

describe('BusinessRisks', () => {
  it('Should render 2 risks', () => {
    const { getByText } = setup({ ...props })
    expect(getByText('Risk 1'))
    expect(getByText('Risk 2'))
  })

  it('Should add a Risk', async () => {
    Services.apiModelObjectManage = jest.fn(() =>
      Promise.resolve(
        {
          companyexportplan: 1,
          model_name,
          pk: 62,
          risk: '',
          contingency_plan: '',
          risk_likelihood: '',
          risk_impact: '',
        },
        'POST'
      )
    )

    const { getByText, queryByText } = setup({
      ...props,
    })
    fireEvent.click(getByText('Add a risk'))

    expect(queryByText('Risk 3')).not.toBeInTheDocument()
    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        {
          companyexportplan: 1,
          model_name,
        },
        'POST'
      )
      expect(getByText('Risk 1'))
      expect(getByText('Risk 2'))
      expect(getByText('Risk 3'))
    })
  })

  it('Should delete a risk', async () => {
    Services.apiModelObjectManage = jest.fn(() => Promise.resolve())
    const { container, getByText, queryByText } = setup({ ...props })
    const button = container.querySelectorAll('.button--delete')[0]
    fireEvent.click(button)
    expect(getByText('Risk 2'))
    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        {
          model_name,
          pk: 60,
        },
        'DELETE'
      )
      expect(queryByText('Risk 2')).not.toBeInTheDocument()
    })
  })

  it('Should update a risk', async () => {
    Services.apiModelObjectManage = jest.fn(() => Promise.resolve())
    const { container } = setup({ ...props })
    const textarea = container.querySelectorAll('textarea')[0]
    fireEvent.change(textarea, {
      target: { value: 'New risk' },
    })

    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        {
          companyexportplan: 1,
          model_name,
          pk: 60,
          risk: 'New risk',
          contingency_plan: 'Contingency plan note',
          risk_impact: 'SEVERE',
          risk_likelihood: 'RARE',
        },
        'PATCH'
      )
      expect(textarea.value).toEqual('New risk')
    })
  })
})
