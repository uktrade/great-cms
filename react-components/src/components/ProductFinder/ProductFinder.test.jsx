/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import ProductFinder from '@src/components/ProductFinder/ProductFinder'
import Services from '@src/Services'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'

let container

const mockResponse = {
  data:{
    txId: '123456',
    currentQuestionInteraction: {
      id:'question_id',
      label: 'item_to_select',
      selectedString: '',
      type: 'SELECTION',
      attrs:[
        {
          id:'attrId1',
          name: 'name_1',
          value: 'false',
        },
        {
          id:'attrId2',
          name: 'name_2',
          value: 'true',
        }        
      ]
    }
  }
}

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
  container.innerHTML = '<span id="set-product-button" data-text="my product"></span>'
  Services.setConfig({apiLookupProductUrl:'/api/lookup-product/'})
  fetchMock.post(/\/api\/lookup-product\//, mockResponse)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
  jest.clearAllMocks()
})

it('Opens and closes product finder', () => {

  act(() => {
    ProductFinder({element:container})
  })
  expect(document.body.querySelector('.product-finder')).toBeFalsy()
  const button = container.querySelector('button')

  act(() => {
    Simulate.click(button)
  })
  const finder = document.body.querySelector('.product-finder');
  const closeButton = finder.querySelector('button.dialog-close');
  expect(document.body.querySelector('.product-finder')).toBeTruthy()
  act(() => {
    Simulate.click(closeButton)
  })
  expect(document.body.querySelector('.product-finder')).toBeFalsy()
})

it('Does a search', async () => {
  act(() => {
    ProductFinder({element:container})
    const button = container.querySelector('button')
    Simulate.click(button)
  })
  expect(document.body.querySelector('.product-finder')).toBeTruthy()  
  const finder = document.body.querySelector('.product-finder');
  const textInput = finder.querySelector('input[type=text]');
  const searchButton = finder.querySelector('button.search-button');
  expect(searchButton.disabled).toBeTruthy()
  textInput.value='cheese'
  Simulate.change(textInput) // the search button is disabled until search term entered
  expect(searchButton.disabled).toBeFalsy()
  act(() => {
    Simulate.click(searchButton)
  })
  await waitFor(() => {
      let results = finder.querySelector('.scroll-area div');
      expect(results).toBeTruthy()
  })
  const radios = finder.querySelectorAll('.scroll-area div input[name=question_id]')
  expect(radios.length).toEqual(2)
  expect(radios[0].closest('label').textContent).toMatch('Name 1') // check spaces and capitalization
  expect(radios[1].closest('label').textContent).toMatch('Name 2')
  const interactionName = radios[1].closest('.interaction').querySelector('.interaction-name')
  expect(interactionName.textContent).toMatch('Item to select')
})
