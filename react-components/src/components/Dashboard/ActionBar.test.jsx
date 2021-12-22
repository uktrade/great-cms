import React from 'react'
import { render, fireEvent, within } from '@testing-library/react'
import fetchMock from 'fetch-mock'

import { Provider } from 'react-redux'
import ReactModal from 'react-modal'

import Services from '@src/Services'
import actions from '@src/actions'

import ActionBar from './ActionBar'

const confirmationTitle =
  'Are you sure you want to delete export plan for selling Acme test product to Testrovia?'

const exportPlanProgress = {
  sectionProgress: [{ populated: 1 }, { populated: 3 }],
  sectionsCompleted: 7,
}

  const assignMock = jest.fn()

  delete window.location
  window.location = { assign: assignMock }


const setup = () => {

  Services.store.dispatch(
    actions.setInitialState({
      exportPlan: {
        name: 'export plan for selling Acme test product to Testrovia',
        product: {
          commodity_code: '123456',
          commodity_name: 'Acme test product',
        },
        market: { country_name: 'Testrovia', country_iso2_code: 'tr' },
      },
    })
  )
  Services.setConfig({
    apiDeleteExportPlanUrl: '/api/export-plan/delete/123/',
  })
  const doc = render(
    <Provider store={Services.store}>
      <ActionBar exportPlanProgress={exportPlanProgress} />
    </Provider>
  )
  ReactModal.setAppElement(doc.baseElement)
  return doc
}

describe('Export Plan delete button', () => {
  it('Should open confirmation', () => {
    const { queryByText, getByText } = setup()
    const button = getByText('Delete plan')
    expect(button).toBeInTheDocument()
    fireEvent.click(button)
    expect(getByText(confirmationTitle)).toBeInTheDocument()
    fireEvent.click(getByText('Cancel'))
    expect(queryByText(confirmationTitle)).toBeFalsy()
  })

  it('Should delete export plan', () => {
    const deleteEp = fetchMock.post(/\/api\/export-plan\/delete\/123\//, {
      pk: 123,
    })
    const container = setup()
    fireEvent.click(container.getByText('Delete plan'))

    const modal = within(
      container.baseElement.querySelector('.ReactModal__Content')
    )
    expect(deleteEp.calls()).toHaveLength(0)
    fireEvent.click(modal.getByText('Delete plan'))
    expect(deleteEp.calls()).toHaveLength(1)
    // Check analytics event...
    expect(window.dataLayer[window.dataLayer.length - 1]).toEqual({
      event: 'deleteExportPlan',
      exportPlanFieldsFilled: 4,
      exportPlanMarketSelected: 'Testrovia',
      exportPlanProductHSCode: '123456',
      exportPlanProductSelected: 'Acme test product',
      exportPlanSectionsComplete: 7,
    })
  })
})
describe('Export Plan download', () => {
  it('Should download export plan', () => {
    const container = setup()
    fireEvent.click(container.getByText('Download plan'))
    expect(window.dataLayer[window.dataLayer.length - 1]).toEqual({
      event: 'downloadExportPlan',
      exportPlanFieldsFilled: 4,
      exportPlanMarketSelected: 'Testrovia',
      exportPlanProductHSCode: '123456',
      exportPlanProductSelected: 'Acme test product',
      exportPlanSectionsComplete: 7,
    })
  })
})
