/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import ProductFinder from '@src/components/ProductFinder/ProductFinderButton'
import ProductFinderModal from '@src/components/ProductFinder/ProductFinderModal'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'


let container

const mockResponse = {
  data: {
    txId: '123456',
    productDescription: 'description',
    knownInteractions: [{
      id: 'known_question_id',
      label: 'Known characteristic',
      selectedString: 'name_1',
      type: 'SELECTION',
      attrs: [{
          id: 'knownId1',
          name: 'known_name_1',
          value: 'false',
        },
        {
          id: 'knownId2',
          name: 'known_name_2',
          value: 'true',
        }
      ]
    }],
    currentQuestionInteraction: {
      id: 'question_id',
      label: 'Current question',
      selectedString: '',
      type: 'SELECTION',
      attrs: [{
          id: 'attrId1',
          name: 'name_1',
          value: 'false',
        },
        {
          id: 'attrId2',
          name: 'name_2',
          value: 'false',
        }
      ]
    }
  }
}

const multiItemResponse = {
  data: {
    txId: '123456',
    productDescription: 'description',
    multiItemError: true
  }
}
describe('Product finder tests', () => {

  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
    container.innerHTML = '<span id="set-product-button" data-productname="my product" data-productcode="123456"></span>'
    Services.setConfig({ apiLookupProductUrl: '/api/lookup-product/' })
    ReactModal.setAppElement(container)
  })

  afterEach(() => {
    // Close the dialogue if it's open
    const closeButton = document.body.querySelector('.product-finder button.dialog-close')
    if (closeButton) {
      act(() => {
        Simulate.click(document.body.querySelector('.product-finder button.dialog-close'))
      })
    }
    document.body.removeChild(container)
    container = null
    fetchMock.restore()
  })

  it('Opens and closes product finder', () => {
    act(() => {
      ProductFinder({ element: container })
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
    fetchMock.post(/\/api\/lookup-product\//, mockResponse)
    act(() => {
      ProductFinder({ element: container })
      const button = container.querySelector('button')
      Simulate.click(button)
    })
    expect(document.body.querySelector('.product-finder')).toBeTruthy()
    const finder = document.body.querySelector('.product-finder');
    const textInput = finder.querySelector('input[type=text]');
    const searchButton = finder.querySelector('button.search-button');
    expect(searchButton.disabled).toBeTruthy()
    textInput.value = 'cheese'
    Simulate.change(textInput) // the search button is disabled until search term entered
    expect(searchButton.disabled).toBeFalsy()
    // trigger search
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
    expect(interactionName.textContent).toMatch('Current question')
  })

  it('Back-tracks search', async () => {
    fetchMock.post(/\/api\/lookup-product\//, mockResponse)
    // Open the dialogue
    act(() => {
      ProductFinder({ element: container })
      const button = container.querySelector('button')
      Simulate.click(button)
    })
    const finder = document.body.querySelector('.product-finder');
    const textInput = finder.querySelector('input[type=text]');
    textInput.value = 'cheese'
    Simulate.change(textInput)
    // Trigger search
    act(() => {
      Simulate.click(finder.querySelector('button.search-button'))
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
    expect(interactionName.textContent).toMatch('Current question')

    expect(document.body.querySelector('.product-finder .interaction-name').textContent).toMatch('Current question')

    const change = finder.querySelector('.change-known-button', document)
    expect(change).toBeTruthy()
    act(() => {
      Simulate.click(change)
    })
    expect(finder.querySelector('.interaction-name').textContent).toMatch('Known characteristic')
  })

  it('Searches multi-item', async () => {
    // Open the dialogue
    fetchMock.post(/\/api\/lookup-product\//, multiItemResponse)
    act(() => {
      ProductFinder({ element: container })
      const button = container.querySelector('button')
      Simulate.click(button)
    })
    const finder = document.body.querySelector('.product-finder');
    const textInput = finder.querySelector('input[type=text]');
    textInput.value = 'cheese set'
    Simulate.change(textInput)
    // Trigger search
    act(() => {
      Simulate.click(finder.querySelector('button.search-button'))
    })
    await waitFor(() => {
      let results = finder.querySelector('.scroll-area div');
      expect(results).toBeTruthy()
    })
    expect(finder.querySelector('.box').textContent).toMatch(/^The item you are classifying is considered a complex item/)
  })

  it('Opens product view and renames product', async () => {
    // Populate existing product, check for naming screen (rather than search screen) 
    // and ability to rename
    
    // set up existing product in store
    let selectedProduct = {
      commodity_code: '123456',
      commodity_name: 'my product'
    }
    Services.store.dispatch(actions.setInitialState({exportPlan:{products:[selectedProduct]}}))


    const setIsOpen = jest.fn()
    // Mock the classification tree request
    Services.setConfig({ apiLookupProductScheduleUrl: '/api/lookup-product-schedule/' })
    
    fetchMock.get(/\/api\/lookup-product-schedule\//, {
      type:'one',
      children:[]
    })

    act(() => {
      ProductFinder({ element: container })
      const button = container.querySelector('button')
      Simulate.click(button)      
    })
    const finder = document.body.querySelector('.product-finder');
    await waitFor(() => {
      let results = finder.querySelector('.scroll-area div');
      expect(results).toBeTruthy()
    })
    const box = finder.querySelector('.box');
    expect(box.querySelector('h3').textContent).toMatch('HS Code: 123456')
    expect(box.querySelector('input').getAttribute('value')).toMatch('my product')
  })

})
