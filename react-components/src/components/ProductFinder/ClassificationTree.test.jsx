import React from 'react'
import fetchMock from 'fetch-mock'
import { render, waitFor } from '@testing-library/react'

import Services from '@src/Services'
import ClassificationTree from './ClassificationTree'

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
    Services.setConfig({
      apiLookupProductScheduleUrl: '/api/lookup-product-schedule/',
    })
  })

  afterEach(() => {
    fetchMock.restore()
  })

  it('Renders a spinner while fetching schedule', async () => {
    fetchMock.get(/\/api\/lookup-product-schedule\//, mockResponse)

    const { container } = render(<ClassificationTree hsCode="123456" />)

    expect(container.querySelector('.spinner')).toBeTruthy()

    await waitFor(() => container.querySelector('.classification-tree'))
  })

  it('Renders a classification tree from type CHAPTER', async () => {
    fetchMock.get(/\/api\/lookup-product-schedule\//, mockResponse)

    const { container, queryByText } = render(<ClassificationTree hsCode="123456" />)

    await waitFor(() => {
      expect(container.querySelector('.classification-tree')).toBeTruthy()
    })

    expect(queryByText('LIVE ANIMALS; ANIMAL PRODUCTS', { exact: false })).toBeNull()

    const levels = container.querySelectorAll('.classification-tree .grid')

    expect(levels).toHaveLength(3)
    expect(levels[0].textContent).toMatch('Dairy produce; birds\' eggs; natural honey; edible products of animal origin, not elsewhere specified or included')
    expect(levels[1].textContent).toMatch('Cheese and curd.')
    expect(levels[2].textContent).toMatch('Processed cheese, not grated or powdered')
  })

  it('Renders an error', async () => {
    fetchMock.get(/\/api\/lookup-product-schedule\//, mockErrorResponse)

    const { container } = render(<ClassificationTree hsCode="123462" />)

    await waitFor(() => {
      expect(container.querySelector('.classification-tree').textContent).toMatch(
        'Unable to show classification tree',
      )
    })
  })
})
