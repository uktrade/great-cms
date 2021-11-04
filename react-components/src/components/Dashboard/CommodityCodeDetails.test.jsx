import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'
import fetchMock from 'fetch-mock'

import Services from '@src/Services'

import CommodityCodeDetails from './CommodityCodeDetails'

const testProduct = {
  commodity_code: '123456',
  commodity_name: 'noname',
}
const setup = () => {
  Services.setConfig({
    apiLookupProductScheduleUrl: '/api/lookup-product-schedule/',
  })
  return render(<CommodityCodeDetails product={testProduct} />)
}

describe('Commodity code details', () => {
  it('Should open details', async () => {
    const mockGetDetails = fetchMock.get(/\/api\/lookup-product-schedule\//, {})
    const { getByText, baseElement } = setup()
    const span = getByText('HS6 code: 123456')
    const button = span.closest('div').querySelector('button')
    expect(button).toBeTruthy()
    fireEvent.click(button)
    waitFor(() => {
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
