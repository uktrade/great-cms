import React from 'react'
import { render, fireEvent, within} from '@testing-library/react'
import fetchMock from 'fetch-mock'

import { Provider } from 'react-redux'
import ReactModal from 'react-modal'

import Services from '@src/Services'
import actions from '@src/actions'

import DeleteButton from './DeleteButton'

const confirmationTitle = 'Are you sure you want to delete export plan for selling Acme test product to Testrovia?'

const setup = () => {
Services.store.dispatch(
  actions.setInitialState({exportPlan: {product:{commodity_code:'123456', commodity_name:'Acme test product'},market:{country_name:'Testrovia', country_iso2_code:'tr'}}})
  )
  Services.setConfig({
    apiDeleteExportPlanUrl: '/api/export-plan/delete/123/',
  })
const doc = render(<Provider store={Services.store}><DeleteButton/></Provider>)
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
      const deleteEp = fetchMock.post(/\/api\/export-plan\/delete\/123\//, {pk:123})
      const container = setup()
      fireEvent.click(container.getByText('Delete plan'))

      const modal = within(container.baseElement.querySelector('.ReactModal__Content'))
      expect(deleteEp.calls()).toHaveLength(0)
      fireEvent.click(modal.getByText('Delete plan'))
      expect(deleteEp.calls()).toHaveLength(1)
    })
})
