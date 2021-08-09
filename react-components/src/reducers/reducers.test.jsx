/* eslint-disable */
import React from 'react'
import { render, waitFor, fireEvent } from '@testing-library/react'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import api from '@src/api'
import { getProducts } from '@src/reducers'

const updateUserData = jest.fn()

const initialProducts = [{
  commodity_code: '123456',
  commodity_name: 'my product',
}]
const newProducts = [{
  commodity_code: '123457',
  commodity_name: 'new product',
}]
describe('Reducers', () => {
  it('tests userSettings reducer', async () => {
    Services.setConfig({
      refreshOnMarketChange: true,
      apiUserDataUrl: '/api/user-data/-name-',
    })
    api.reloadPage = jest.fn()

    Services.store.dispatch(
      actions.setInitialState({ userSettings: { UserProducts: initialProducts } })
    )
    api.setUserData = (payload) => {
      return new Promise((resolve) => {
        resolve(updateUserData(payload))
      })
    }
    expect(Services.store.getState().userSettings.UserProducts).toEqual(initialProducts)
    Services.store.dispatch(actions.setUserData('UserProducts', newProducts))
    await waitFor(() => {
      expect(updateUserData).toHaveBeenCalledTimes(1)
    })
    expect(api.reloadPage).toHaveBeenCalledTimes(1)
    expect(Services.store.getState().userSettings.UserProducts).toEqual(newProducts)
  })
})
