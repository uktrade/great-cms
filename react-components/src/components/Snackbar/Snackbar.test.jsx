/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import Services from '@src/Services'
import actions from '@src/actions'
import { waitFor } from '@testing-library/react'
import createSnackbar from '@src/components/Snackbar/Snackbar'

let container

describe('Test snackbar', () => {
  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
  })

  it('Opens Snackbar', () => {
    act(() => {
      createSnackbar({
        element: container,
      })
    })
    const sbOuter = container.querySelector('.snackbar')
    expect(sbOuter).toBeTruthy()
    Services.store.dispatch(actions.notify('message', `Some text message 1`))
      expect(sbOuter.querySelector('.snackbar-message')).toBeTruthy()
    expect(sbOuter.querySelector('.snackbar-message').textContent).toMatch('Some text message 1')
  })
})
