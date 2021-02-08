/* eslint-disable */
import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import fetchMock from 'fetch-mock'
import Services from '@src/Services'
import { waitFor } from '@testing-library/react'
import { act, Simulate } from 'react-dom/test-utils'
import ClassificationTree from './ClassificationTree'

let container

const mockResponse = {
  uom: null,
  duties: null,
  errorCode: null,
  desc: null,
  code: null,
  errorMessage: null,
  id: null,
  type: null,
  children: [
    {
      children: [
        {
          children: [
            {
              children: [
                {
                  children: [],
                  desc: '- Processed cheese, not grated or powdered',
                  code: '040630',
                  errorMessage: null,
                  id: '040630',
                  type: 'ITEM',
                },
              ],
              desc: 'cheese and curd.',
              code: '0406',
              type: 'HEADING',
            },
          ],
          desc:
            "CHAPTER 4 - DAIRY PRODUCE; BIRDS' EGGS; NATURAL HONEY; EDIBLE PRODUCTS OF ANIMAL ORIGIN, NOT ELSEWHERE SPECIFIED OR INCLUDED",
          code: '04',
          type: 'CHAPTER',
        },
      ],
      desc: 'SECTION I - LIVE ANIMALS; ANIMAL PRODUCTS',
      code: 'I',
      errorMessage: null,
      id: '00_01',
      type: 'SECTION',
    },
  ],
}

const mockErrorResponse = {
  uom: null,
  duties: null,
  errorCode: 123,
  desc: null,
  code: null,
  errorMessage: 'Invalid code',
  id: null,
  type: null,
  children: [],
}
describe('Classification tree', () => {
  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
    Services.setConfig({
      apiLookupProductScheduleUrl: '/api/lookup-product-schedule/',
    })
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    fetchMock.restore()
  })

  it('Classification tree Renders a classification tree', async () => {
    const hsCode = '123456'
    fetchMock.get(/\/api\/lookup-product-schedule\//, mockResponse)

    act(() => {
      ReactDOM.render(<ClassificationTree hsCode={hsCode} />, container)
    })
    await waitFor(() => {
      let results = container.querySelector('.classification-tree__item')
      expect(results).toBeTruthy()
    })
    let arrows = container.querySelectorAll('.classification-tree__arrow')
    expect(arrows.length).toEqual(2)
    let levels = container.querySelectorAll('.classification-tree__item > span')
    expect(levels.length).toEqual(3)
    expect(levels[2].textContent).toMatch(
      'Processed cheese, not grated or powdered'
    )
    expect(levels[1].textContent).toMatch('Cheese and curd.')
    expect(levels[0].textContent).toMatch(
      "Dairy produce; birds' eggs; natural honey; edible products of animal origin, not elsewhere specified or included"
    )
  })

  it('Classification tree Renders an error', async () => {
    fetchMock.get(/\/api\/lookup-product-schedule\//, mockErrorResponse)
    act(() => {
      ReactDOM.render(<ClassificationTree hsCode={'123462'} />, container)
    })
    await waitFor(() => {
      let results = container.querySelector('.classification-tree')
      expect(results && results.textContent).toMatch(
        'Unable to show classification tree'
      )
    })
  })
})
