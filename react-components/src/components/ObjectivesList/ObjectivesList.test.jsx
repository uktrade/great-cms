import React from 'react'

import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetchMock from 'fetch-mock'
import { fakeSchedulers } from 'rxjs-marbles/jest'

import { ObjectivesList } from '@src/components/ObjectivesList'
import Field from '@src/components/Fields/Field'
import Services from '@src/Services'

Enzyme.configure({ adapter: new Adapter() })

let wrapper;

const dummyObjectiveOne = {
  description: 'Some text',
  owner: 'Jane Doe',
  planned_reviews: 'Lorem ipsum',
  start_date: '',
  end_date: '',
  companyexportplan: 1,
  pk: 1,
  isLoading: false,
  showSavedMessage: false,
  errors: {},
}

const dummyObjectiveTwo = {
  description: 'Some text',
  owner: 'Jane Doe',
  planned_reviews: 'Lorem ipsum',
  start_date: '',
  end_date: '',
  companyexportplan: 1,
  pk: 2,
  isLoading: false,
  showSavedMessage: false,
  errors: {},
}

const dummyObjectiveThree = {
  description: '',
  owner: '',
  planned_reviews: 'Lorem ipsum',
  start_date: '',
  end_date: '',
  companyexportplan: 1,
  pk: 3,
  isLoading: false,
  showSavedMessage: false,
  errors: {},
}

const objectives = [dummyObjectiveOne, dummyObjectiveTwo, dummyObjectiveThree]

beforeEach(() => {
  jest.useFakeTimers()
  fetchMock.reset()

  wrapper = Enzyme.mount(
    <ObjectivesList
      objectives={objectives}
      exportPlanID={1}
    />
  )

  Services.setConfig({
    apiObjectivesCreateUrl: 'http://www.example.com/export-plan/api/objectives/create/',
    apiObjectivesDeleteUrl: 'http://www.example.com/export-plan/api/objectives/delete/',
    apiObjectivesUpdateUrl: 'http://www.example.com/export-plan/api/objectives/update/',
  })

})

afterEach(() => {
  jest.useRealTimers()
})

describe('ObjectivesList', () => {
  test('should generate objective form fields from props and prepopulate', () => {

    const descriptionField = (
      <Field
        id='description_1'
        type='textarea'
        placeholder='Add some text'
        label='Description'
        name='description'
        value={dummyObjectiveOne.description}
      />
    )

    const ownerField = (
      <Field
        id='owner_1'
        type='textarea'
        placeholder='Add an owner'
        label='Owner'
        name='owner'
        value={dummyObjectiveOne.owner}
      />
    )

    expect(wrapper.state('objectives')).toEqual(objectives)
    expect(wrapper.containsMatchingElement(descriptionField)).toEqual(true)
    expect(wrapper.containsMatchingElement(ownerField)).toEqual(true)
  })

  test('should update objectives list state on change', () => {

    const input = wrapper.find('#description_1 textarea')

    // change value of form field
    const dummyEvent = {
      target: {name: 'description', value: 'Lorem ipsum'}
    }

    input.simulate('change', dummyEvent)

    const updatedObjective = {...dummyObjectiveOne}
    updatedObjective.description = 'Lorem ipsum'

    const updatedObjectives = [updatedObjective, dummyObjectiveTwo, dummyObjectiveThree]

    // check objectives state has changed
    expect(wrapper.state('objectives')).toStrictEqual(updatedObjectives)

  })

  test('should debounce input and show saved message', () => {

    fetchMock.post(Services.config.apiObjectivesUpdateUrl, 200)

    const input = wrapper.find('#description_1 textarea')

    expect(wrapper.state('objectives')[0].isLoading).toBe(false)

    // change value of form field
    const dummyEvent = {
      target: {name: 'description', value: 'Lorem ipsum'}
    }

    fakeSchedulers((advance) => {
      input.simulate('change', dummyEvent)

      // wait for debounce
      advance(1000 * 3)
      expect(wrapper.state('objectives')[0].isLoading).toBe(true)
      expect(wrapper.state('objectives')[0].showSavedMessage).toBe(true)
    })

    fakeSchedulers((advance) => {
      // wait for saved message to hide
      advance(1000 * 3)
      expect(wrapper.state('objectives')[0].isLoading).toBe(false)
      expect(wrapper.state('objectives')[0].showSavedMessage).toBe(false)
    })

  })

})
