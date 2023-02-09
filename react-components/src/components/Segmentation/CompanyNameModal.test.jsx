/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'

import { act, Simulate } from 'react-dom/test-utils'
import { waitFor, fireEvent, getByLabelText } from '@testing-library/react'
import CompanyNameModal from '@src/components/Segmentation/CompanyNameModal'
import Services from '@src/Services'
import fetchMock from 'fetch-mock'
import reactModal from 'react-modal'

let container
let getChData

const question = {
  id: 1,
  name: 'company',
  title: 'Business Name',
  type: 'COMPANY_LOOKUP',
  choices: {
    placeholder: 'Business name',
    manualContent:
      'Please type in your official business name. If you are a sole trader, your business name may be the same as your name.',
    reviewContent:
      'Verify that we have imported the correct company from Companies House for your business. <p class="body-m m-t-xs">Note that any incorrect details for your company need to be corrected with Companies House. </p>',
    searchContent:
      'Begin by typing the first few letters of your business name as registered with Companies House.',
    reviewFromProfileContent:
      'We\u2019ve retrieved information from Companies House for the business you\u2019ve saved in your profile. If this is the right company, select \u2018Next\u2019. Otherwise select \u2018Search\u2019 to find the correct company. <p class="body-m m-t-xs">Note that any incorrect details for your company need to be corrected with Companies House. </p>',
  },
}

const mockChResponse = {
  items: [
    {
      company_name: 'Company 1',
      company_number: '123456789a',
      date_of_creation: '2015-05-12',
    },
    { company_name: 'Company 2', company_number: '123456789b' },
  ],
}

const profileResponse = {
  company_name: 'Company 1',
  company_number: '123456789a',
  sic_codes: ['123456'],
}

beforeEach(() => {
  reactModal.setAppElement(document.body)
  container = document.createElement('div')
  document.body.appendChild(container)
  Services.setConfig({ apiCompaniesHouseUrl: '/api/ch-house/' })
  Services.setInitialState({ exportPlan: { markets: [] } })
  getChData = fetchMock.get(
    /\/api\/ch-house\//,
    Object.assign({}, mockChResponse)
  )
})

afterEach(() => {
  document.body.removeChild(container)
  document.body.innerHTML = '' // this is crucial as the modal is in a portal and will not be removed when the container is removed
  jest.clearAllMocks()
  getChData.reset()
})

describe('Test company search modal', () => {
  it('Does a company search', async () => {
    const setValue = jest.fn()
    const nextButtonClick = jest.fn()
    const backButtonClick = jest.fn()
    const closeClick = jest.fn()

    act(() => {
      ReactDOM.render(
        <CompanyNameModal
          question={question}
          value={''}
          setValue={setValue}
          nextButtonClick={nextButtonClick}
          backButtonClick={backButtonClick}
          closeClick={closeClick}
          progressPercentage={60}
        />,
        container
      )
    })
    // Should have rendered in search mode
    await waitFor(() => {
      expect(document.body.querySelector('.segmentation-modal')).toBeTruthy()
    })
    let modal = document.body.querySelector('.segmentation-modal')
    let input = modal.querySelector('.select__placeholder--input input')
    expect(input).toBeTruthy()

    // Click back
    expect(backButtonClick).toHaveBeenCalledTimes(0)
    act(() => {
      Simulate.click(modal.querySelector('.button--tertiary'))
    })
    expect(backButtonClick).toHaveBeenCalledTimes(1)
    // click close
    expect(closeClick).toHaveBeenCalledTimes(0)
    act(() => {
      Simulate.click(modal.querySelector('#dialog-close'))
    })
    expect(closeClick).toHaveBeenCalledTimes(1)
    // click next - it's disabled so nothing happens
    expect(modal.querySelector('.primary-button').disabled).toBeTruthy()
    fireEvent.change(input, { target: { value: 'ABC' } })
    await waitFor(() => {
      expect(getChData.calls().length).toEqual(1)
    })
    expect(modal.querySelector('.select__list').textContent).toMatch(
      'Company 1'
    )
    expect(modal.querySelector('.select__list').textContent).toMatch(
      'Company number: 123456789b'
    )
    // Select a company
    getChData.reset()
    getChData = fetchMock.get(
      /\/api\/ch-house\//,
      Object.assign({}, profileResponse)
    )
    //
    act(() => {
      Simulate.click(modal.querySelector('.select__list li'))
    })
    expect(input.value).toMatch('Company 1')
    // check that the next button is enabled
    await waitFor(() => {
      expect(modal.querySelector('.primary-button').disabled).toBeFalsy()
    })
    // Click next to save
    act(() => {
      Simulate.click(modal.querySelector('.primary-button'))
    })
    await waitFor(() => {
      expect(modal.querySelector('.g-panel')).toBeTruthy()
    })
    const reviewText = modal.querySelector('.g-panel').textContent
    expect(reviewText).toMatch('Company nameCompany 1')
    expect(reviewText).toMatch('Company number123456789a')
    expect(reviewText).toMatch('Incorporated on12 May 2015')
    // click next again and save the company
    act(() => {
      Simulate.click(modal.querySelector('.primary-button'))
    })
    expect(nextButtonClick).toHaveBeenCalledTimes(1)
  })

  it('Allows user to type company name', async () => {
    const setValue = jest.fn()
    const nextButtonClick = jest.fn()
    const backButtonClick = jest.fn()
    const closeClick = jest.fn()

    act(() => {
      ReactDOM.render(
        <CompanyNameModal
          question={question}
          value={''}
          setValue={setValue}
          nextButtonClick={nextButtonClick}
          backButtonClick={backButtonClick}
          closeClick={closeClick}
          progressPercentage={60}
        />,
        container
      )
    })
    // Should have rendered in search mode
    let modal
    await waitFor(() => {
      modal = document.body.querySelector('.segmentation-modal')
      expect(modal).toBeTruthy()
    })

    expect(modal.querySelector('button.link').textContent).toMatch(
      'I cannot find my business name'
    )
    // Click to manual
    act(() => {
      Simulate.click(modal.querySelector('button.link'))
    })
    expect(modal.querySelector('button .link').textContent).toMatch(
      'My business is registered with'
    )
    // next button disabled
    expect(modal.querySelector('.primary-button').disabled).toBeTruthy()
    let input = modal.querySelector('input#company_name')
    expect(input).toBeTruthy()
    // button should only enable when three chars are typed
    act(() => {
      fireEvent.change(input, { target: { value: 'AB' } })
    })
    // check the value
    expect(setValue).toHaveBeenCalledTimes(1)
    expect(setValue.mock.calls[0][0]).toEqual({ company_name: 'AB' })

    expect(modal.querySelector('.primary-button').disabled).toBeTruthy()
    act(() => {
      fireEvent.change(input, { target: { value: 'Company 1' } })
    })
    expect(setValue).toHaveBeenCalledTimes(2)
    expect(setValue.mock.calls[1][0]).toEqual({ company_name: 'Company 1' })
    // Next button now enabled
    expect(modal.querySelector('.primary-button').disabled).toBeFalsy()
    act(() => {
      Simulate.click(modal.querySelector('.primary-button'))
    })
    expect(nextButtonClick).toHaveBeenCalledTimes(1)
  })
})
