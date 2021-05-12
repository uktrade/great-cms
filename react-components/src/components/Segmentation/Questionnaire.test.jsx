/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import { waitFor, fireEvent, getByLabelText } from '@testing-library/react'
import Questionnaire from '@src/components/Segmentation/Questionnaire'
import Services from '@src/Services'
import fetchMock from 'fetch-mock'
import reactModal from 'react-modal'

let container
let postQuestionnaire
let getQuestionnaire

const mockResponse = {
  questions: [
    {
      id: 1,
      order: 1,
      name: 'question 1',
      title: 'Question 1?',
      type: 'RADIO',
      choices: {
        options: [
          {
            label: 'Option 1',
            value: '1111',
          },
          {
            label: 'Option2',
            value: '2',
            jump:'end',
          },
        ],
      },
    },
    {
      id: 2,
      order: 2,
      name: 'question 2',
      title: 'Question 2?',
      type: 'SELECT',
      choices: {
        placeholder: 'Select placeholder',
        options: [
          {
            label: 'Option 1',
            value: '1',
          },
          {
            label: 'Option2',
            value: '2',
          },
        ],
      },
    },
  ],
  answers: [],
}

const mockResponseAnswer2 = { answers: [{ question_id: 1, answer: '1111' }] }
const mockResponseAnswer3 = { answers: [{ question_id: 1, answer: '2' }] }



describe('VFM Questionnaire', () => {

  beforeEach(() => {
    reactModal.setAppElement(document.body)
    container = document.createElement('div')
    document.body.appendChild(container)
    Services.setConfig({ apiUserQuestionnaireUrl: '/api/user-questionnaire/' })
    Services.setInitialState({ exportPlan: { markets: [] } })
    getQuestionnaire = fetchMock.get(
      /\/api\/user-questionnaire\//,
      Object.assign({}, mockResponse)
    )
    postQuestionnaire = fetchMock.post(
      /\/api\/user-questionnaire\//,
      Object.assign({}, mockResponse, mockResponseAnswer2)
    )
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    jest.clearAllMocks()
    getQuestionnaire.reset()
    postQuestionnaire.reset()
  })

  it('Opens and closes', async () => {
    const handleModalClose = jest.fn()

    act(() => {
      ReactDOM.render(
        <Questionnaire handleModalClose={handleModalClose} />,
        container
      )
    })
    await waitFor(() => {
      expect(getQuestionnaire.calls().length).toEqual(1)
      expect(document.body.querySelector('.segmentation-modal')).toBeTruthy()
    })
    let modal = document.body.querySelector('.segmentation-modal')
    expect(modal).toBeTruthy()
    // Click not now -> dismiss
    act(() => {
      Simulate.click(modal.querySelector('.button--tertiary'))
    })
    await waitFor(() => {
      expect(document.body.querySelector('.segmentation-modal')).toBeFalsy()
    })
  })

  it('Answers question', async () => {
    const handleModalClose = jest.fn()

    act(() => {
      ReactDOM.render(
        <Questionnaire handleModalClose={handleModalClose} />,
        container
      )
    })
    await waitFor(() => {
      expect(getQuestionnaire.calls().length).toEqual(1)
      expect(document.body.querySelector('.segmentation-modal')).toBeTruthy()
    })
    let modal = document.body.querySelector('.segmentation-modal')
    // Click continue
    act(() => {
      Simulate.click(modal.querySelector('.button--primary'))
    })
    await waitFor(() => {
      expect(document.body.querySelector('h3').textContent).toMatch(
        'Question 1?'
      )
    })
    // check progress bar
    expect(
      window.getComputedStyle(modal.querySelector('.progress-bar span')).width
    ).toEqual('0%')
    // check 'continue' is disabled
    expect(modal.querySelector('.button--primary').disabled).toBeTruthy()
    // Click a radio button
    act(() => {
      Simulate.click(modal.querySelector('.multiple-choice input'))
    })
    await waitFor(() => {
      expect(modal.querySelector('.button--primary').disabled).toBeFalsy()
    })

    expect(postQuestionnaire.calls().length).toEqual(1)
    act(() => {
      Simulate.click(modal.querySelector('.button--primary'))
    })
    await waitFor(() => {
      expect(postQuestionnaire.calls().length).toEqual(2)
    })
    expect(document.body.querySelector('h3').textContent).toMatch('Question 2?')
    expect(
      modal.querySelector('.select__placeholder--value').textContent
    ).toMatch('Select placeholder')
    expect(
      window.getComputedStyle(modal.querySelector('.progress-bar span')).width
    ).toEqual('50%')
    // Go back
    act(() => {
      Simulate.click(modal.querySelector('.button--tertiary'))
    })
    await waitFor(() => {
      expect(document.body.querySelector('h3').textContent).toMatch('Question 1?')
    })
    // Go back to start
    act(() => {
      Simulate.click(modal.querySelector('.button--tertiary'))
    })
    expect(document.body.querySelector('h3').textContent).toMatch('Help us serve you better')
    // close
    act(() => {
      Simulate.click(modal.querySelector('.dialog-close'))
    })
    await waitFor(() => {
      expect(document.body.querySelector('.segmentation-modal')).toBeFalsy()
    })
  })

  it('Goes to end and back', async () => {
    const handleModalClose = jest.fn()

    act(() => {
      ReactDOM.render(
        <Questionnaire handleModalClose={handleModalClose} />,
        container
      )
    })
    await waitFor(() => {
      expect(getQuestionnaire.calls().length).toEqual(1)
      expect(document.body.querySelector('.segmentation-modal')).toBeTruthy()
    })
    let modal = document.body.querySelector('.segmentation-modal')
    // Click continue
    act(() => {
      Simulate.click(modal.querySelector('.button--primary'))
    })
    await waitFor(() => {
      expect(document.body.querySelector('h3').textContent).toMatch(
        'Question 1?'
      )
    })
    // Click a radio button
    act(() => {
      Simulate.click(modal.querySelector('.multiple-choice input'))
    })
    await waitFor(() => {
      expect(modal.querySelector('.button--primary').disabled).toBeFalsy()
    })
    // Prepare post with final question answered
    postQuestionnaire.reset()
    postQuestionnaire = fetchMock.post(
      /\/api\/user-questionnaire\//,
      Object.assign({}, mockResponse, mockResponseAnswer3)
    )
    act(() => {
      Simulate.click(modal.querySelector('.button--primary'))
    })
    await waitFor(() => {
      expect(document.body.querySelector('h3').textContent).toMatch('Thank you')
    })
    // We're on the final page.  Try the back button from here
    act(() => {
      Simulate.click(modal.querySelector('.button--tertiary'))
    })
    await waitFor(() => {
      expect(document.body.querySelector('h3').textContent).toMatch('Question 1?')
    })
  })
})
