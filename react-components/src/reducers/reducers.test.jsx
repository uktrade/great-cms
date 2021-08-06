/* eslint-disable */
import React from 'react'
import { render, waitFor, fireEvent } from '@testing-library/react'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import api from '@src/api'
import { getProducts } from '@src/reducers'

const updateUserData = jest.fn()

const selectedProduct = {
  commodity_code: '123456',
  commodity_name: 'my product',
}

describe('Reducers', () => {
  xit('tests userBasket reducer', async () => {
    let data = [{ commodity_name: 'Test product', commodity_code: '123456' }]
    Services.setConfig({
      refreshOnMarketChange: true,
      apiUserDataUrl: '/api/user-data/-name-',
    })
    Services.store.dispatch(
      actions.setInitialState({ userSettings: { UserProducts: [selectedProduct] } })
    )
    api.setUserData = (payload) => {
      return new Promise((resolve) => {
        resolve(updateUserData(payload))
      })
    }
    api.reloadPage = jest.fn()
    Services.store.dispatch(actions.setProducts(data))
    await waitFor(() => {
      expect(updateUserData).toHaveBeenCalledTimes(1)
      expect(api.reloadPage).toHaveBeenCalledTimes(0)
    })
    expect(getProducts(Services.store.getState())).toEqual(data)
    // No Change to code
    data = { ...data, commodity_name: 'New Name' }
    Services.store.dispatch(actions.setProducts(data))
    await waitFor(() => {
      expect(updateUserData).toHaveBeenCalledTimes(2)
      expect(api.reloadPage).toHaveBeenCalledTimes(1)
    })
    expect(getProducts(Services.store.getState())).toEqual(data)
    data = { ...data, commodity_code: '654321' }
    Services.store.dispatch(actions.setProducts(data))
    await waitFor(() => {
      expect(updateUserData).toHaveBeenCalledTimes(3)
      expect(api.reloadPage).toHaveBeenCalledTimes(2)
    })
    expect(getProducts(Services.store.getState())).toEqual(data)
    // test no refesh if config not set
    Services.setConfig({
      refreshOnMarketChange: false,
    })
    data = { ...data, commodity_code: '999999' }
    Services.store.dispatch(actions.setProducts(data))
    await waitFor(() => {
      expect(updateUserData).toHaveBeenCalledTimes(4)
      expect(api.reloadPage).toHaveBeenCalledTimes(3)
    })
    expect(getProducts(Services.store.getState())).toEqual(data)
  })
})
