import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import { VideoTranscript } from '@src/components/VideoTranscript/VideoTranscript'

let container

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
})

it('toggles transcript text', () => {
  act(() => {
    ReactDOM.render(<VideoTranscript transcript="test transcript" />, container)
  })

  expect(container.querySelectorAll('.video-transcript').length).toEqual(1)
  expect(container.querySelectorAll('.video-transcript__text-area').length).toEqual(0)

  const button = container.querySelector('button')

  act(() => {
    Simulate.click(button)
  })

  expect(container.querySelectorAll('.video-transcript__text-area').length).toEqual(1)

  act(() => {
    Simulate.click(button)
  })

  expect(container.querySelectorAll('.video-transcript__text-area').length).toEqual(0)
})
