import React from 'react'
import { render, waitFor } from '@testing-library/react'
import fetchMock from 'fetch-mock'

import Services from '@src/Services'

import CommodityCodeDetails from './CommodityCodeDetails'

import mockScheduleCheese from '../ProductFinder/fixtures/product-schedule-cheese.json'

const testProduct = {
  commodity_code: '123456',
  commodity_name: 'noname',
}
const setup = () => render(<CommodityCodeDetails product={testProduct} />)

describe('Commodity code details', () => {
  beforeEach(() => {
    Services.setConfig({
      apiLookupProductScheduleUrl: '/api/lookup-product-schedule/',
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('Should open details', async () => {
    const mockGetDetails = fetchMock.get(
      /\/api\/lookup-product-schedule\//,
      mockScheduleCheese
    )
    const { getByText, baseElement } = setup()
    const span = getByText('noname')
    const button = span.closest('div').querySelector('button')

    expect(button).toBeTruthy()

    button.click()

    await waitFor(() => {
      expect(baseElement.querySelector('.classification-tree')).toBeTruthy()
    })
    expect(mockGetDetails.calls()).toHaveLength(1)
    expect(mockGetDetails.calls()[0][0]).toMatch(/\?hs_code=123456/)

    // Check analytics event...
    expect(window.dataLayer[window.dataLayer.length - 1]).toEqual({
      event: 'openProductInfo',
      HS6Code: testProduct.commodity_code,
    })
  })
})
