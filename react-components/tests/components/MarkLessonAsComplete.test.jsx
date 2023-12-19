import React from 'react'
import { render, waitFor } from '@testing-library/react'
import fetchMock from 'fetch-mock'

import { MarkLessonAsComplete } from '@src/components/MarkLessonAsComplete/MarkLessonAsComplete'

const mockResponse = {
  lesson_completed: [{}, {}],
}

describe('MarkLessonAsComplete', () => {
  beforeEach(() => {
    fetchMock.get(
      'http://localhost/sso/api/v1/lesson-completed/20/',
      mockResponse,
      { overwriteRoutes: false }
    )
    fetchMock.post('/sso/api/v1/lesson-completed/20/', mockResponse, {
      overwriteRoutes: false,
    })
    fetchMock.delete('/sso/api/v1/lesson-completed/20/', mockResponse, {
      overwriteRoutes: false,
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders correct elements', async () => {
    const { container } = render(
      <MarkLessonAsComplete endpoint="/sso/api/v1/lesson-completed/20/" />
    )

    await waitFor(() => {
      expect(
        container.querySelectorAll('.govuk-checkboxes__item')
      ).toHaveLength(1)
      expect(container.querySelectorAll('label')).toHaveLength(1)
      expect(container.querySelectorAll('.govuk-checkboxes__input')).toHaveLength(1)
    })
  })

  it('updates label text on click', async () => {
    const { container } = render(
      <MarkLessonAsComplete endpoint="/sso/api/v1/lesson-completed/20/" />
    )

    expect(container.querySelector('label').textContent).toMatch('Yes')

    container.querySelector('input').click()

    await waitFor(() => {
      expect(container.querySelector('label').textContent).toMatch(
        'Progress saved'
      )
    })
  })
})
