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
    "id": 1,
    "name": "company",
    "title": "Business Name",
    "type": "COMPANY_LOOKUP",
    "choices":
    {
      "placeholder": "Business name",
      "manualContent": "Please type in your official business name. If you are a sole trader, your business name may be the same as your name.",
      "reviewContent": "Verify that we have imported the correct company from Companies House for your business. <p class=\"body-m m-t-xs\">Note that any incorrect details for your company need to be corrected with Companies House. </p>",
      "searchContent": "Begin by typing the first few letters of your business name as registered with Companies House.",
      "reviewFromProfileContent": "We\u2019ve retrieved information from Companies House for the business you\u2019ve saved in your profile. If this is the right company, select \u2018Next\u2019. Otherwise select \u2018Search\u2019 to find the correct company. <p class=\"body-m m-t-xs\">Note that any incorrect details for your company need to be corrected with Companies House. </p>"
    },
  }


const mockChResponse = {items:[{company_name:'Company 1',company_number:'123456789a', date_of_creation:'2015-05-12'},
{company_name:'Company 2',company_number:'123456789b'}]}

const profileResponse = {company_name:'Company 1',company_number:'123456789a',sic_codes:['123456']}

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
  console.log('Before each')
})

afterEach(() => {
  console.log('Teardown')
  document.body.removeChild(container)
  container = null
  jest.clearAllMocks()
  getChData.reset()
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
    await waitFor(() => {
      expect(document.body.querySelector('.segmentation-modal')).toBeTruthy()
    })
    let modal = document.body.querySelector('.segmentation-modal')
  console.log(modal.textContent)
    expect(modal.querySelector('button.link').textContent).toMatch('I cannot find my business name')
    // Click to manual
    act(() => {
      Simulate.click(modal.querySelector('button.link'))
    })
    expect(modal.querySelector('button .link').textContent).toMatch('My business is registered with')
    // next button disabled
    expect(modal.querySelector('.button--primary').disabled).toBeTruthy()
    let input = modal.querySelector('input#company_name')
    expect(input).toBeTruthy()
    // button should only enable when three chars are typed
    act(() => {
      fireEvent.change(input, { target: { value: 'AB' } })
    })
    // check the value
    expect(setValue).toHaveBeenCalledTimes(1)
    expect(setValue.mock.calls[0][0]).toEqual({"company_name": "AB"})

    expect(modal.querySelector('.button--primary').disabled).toBeTruthy()
    act(() => {
      fireEvent.change(input, { target: { value: 'Company 1' } })
    })
    expect(setValue).toHaveBeenCalledTimes(2)
    expect(setValue.mock.calls[1][0]).toEqual({"company_name": 'Company 1'})
    // Next button now enabled
    expect(modal.querySelector('.button--primary').disabled).toBeFalsy()
    act(() => {
      Simulate.click(modal.querySelector('.button--primary'))
    })
    expect(nextButtonClick).toHaveBeenCalledTimes(1)
  })
