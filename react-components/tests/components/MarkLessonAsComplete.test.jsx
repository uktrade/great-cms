import React from 'react'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import { act } from 'react-dom/test-utils'
import fetchMock from 'fetch-mock'
import { MarkLessonAsComplete } from '@src/components/MarkLessonAsComplete/MarkLessonAsComplete'

Enzyme.configure({ adapter: new Adapter() })

const mockResponse = {
  lesson_completed: [{}, {}],
}

describe('MarkLessonAsComplete', () => {
  let wrapper
  const nonTickedText = 'Lesson complete?Yes'
  const tickedText = 'Lesson complete?Great! Progress saved'

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
    wrapper = Enzyme.mount(
      <MarkLessonAsComplete endpoint="/sso/api/v1/lesson-completed/20/" />
    )
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders correct elements', async () => {
    await act(async () => {
      expect(wrapper.find('.mark-lesson-as-complete')).toHaveLength(1)
      expect(wrapper.find('h2')).toHaveLength(1)
      expect(wrapper.find('.great-checkbox')).toHaveLength(1)
    })
  })

  it('updates label text', async () => {
    await act(async () => {
      expect(wrapper.find('label').text()).toEqual(nonTickedText)
      await act(async () => {
        wrapper.find('input').props().onChange()
      })

      expect(wrapper.find('label').text()).toEqual(nonTickedText)

      await act(async () => {
        wrapper.find('input').props().onClick()
      })

      expect(wrapper.find('label').text()).toEqual(tickedText)
    })
  })
})
