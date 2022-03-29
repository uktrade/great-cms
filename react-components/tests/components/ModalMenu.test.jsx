import React from 'react'
import { fireEvent, render, waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'
import { Menu } from '@src/components/ModalMenu'

ReactModal.setAppElement('body')

const renderAndOpen = async (component) => {
  const rendered = render(component)

  // Modal is outside of `container` so we have to use `document` here
  expect(document.querySelector('.magna-header__dropdown')).toBeNull()

  rendered.container.querySelector('.magna-header__dropdown-button').click()

  await waitFor(() => document.querySelector('.magna-header__dropdown'))

  return rendered
}

describe('Modal Menu', () => {
  it('opens on click', async () => {
    const { container } = render(<Menu authenticated={false} userName="" />)

    expect(document.querySelector('.magna-header__dropdown')).toBeNull()

    container.querySelector('.magna-header__dropdown-button').click()

    await waitFor(() => {
      expect(document.querySelector('.magna-header__dropdown')).toBeTruthy()
    })
  })

  it('renders the username and signed in menu', async () => {
    const { getByText } = await renderAndOpen(
      <Menu authenticated userName="John" />
    )

    expect(getByText('Hi John')).toBeTruthy()
    expect(getByText('Learn to export')).toBeTruthy()
    expect(getByText('Where to export')).toBeTruthy()
    expect(getByText('Make an export plan')).toBeTruthy()
    expect(getByText('Account')).toBeTruthy()
    expect(getByText('Sign out')).toBeTruthy()
  })

  it('renders a logged out menu', async () => {
    const { getByText } = await renderAndOpen(
      <Menu authenticated={false} userName="" />
    )

    expect(getByText('Send a feedback email')).toBeTruthy()
    expect(getByText('Sign up / Log in')).toBeTruthy()
  })

  describe('closing the menu', () => {
    it('closes when pressing escape', async () => {
      await renderAndOpen(<Menu authenticated={false} userName="" />)

      fireEvent.keyDown(document.querySelector('.magna-header__dropdown'), {
        keyCode: 27,
      })

      await waitFor(() => {
        expect(document.querySelector('.magna-header__dropdown')).toBeNull()
      })
    })

    it('closes when clicking the menu button again', async () => {
      const { container } = await renderAndOpen(
        <Menu authenticated={false} userName="" />
      )

      container.querySelector('.magna-header__dropdown-button').click()

      await waitFor(() => {
        expect(document.querySelector('.magna-header__dropdown')).toBeNull()
      })
    })

    it('closes when clicking the overlay', async () => {
      await renderAndOpen(<Menu authenticated={false} userName="" />)

      document.querySelector('.ReactModal__Overlay').click()

      await waitFor(() => {
        expect(document.querySelector('.magna-header__dropdown')).toBeNull()
      })
    })
  })

  describe('focus trap', () => {
    const tab = (shift = false) => {
      fireEvent.keyDown(document.querySelector('body'), {
        keyCode: 9,
        shiftKey: shift,
      })
    }

    it('keeps the focus within the menu when pressing tab from the menu button', async () => {
      await renderAndOpen(<Menu authenticated={false} userName="" />)
      const button = document.querySelector('.magna-header__dropdown-button')
      button.focus()
      fireEvent.keyDown(button, {
        keyCode: 9,
      })
      expect(document.activeElement.textContent).toBe('Send a feedback email')
    })

    it('keeps the focus within the menu when pressing shift-tab from the menu button', async () => {
      await renderAndOpen(<Menu authenticated={false} userName="" />)
      const button = document.querySelector('.magna-header__dropdown-button')
      button.focus()
      fireEvent.keyDown(button, {
        keyCode: 9,
        shiftKey: true,
      })
      expect(document.activeElement.textContent).toBe('Sign up / Log in')
    })
  })
})
