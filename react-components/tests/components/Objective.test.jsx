import React from 'react'

import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetchMock from 'fetch-mock'

import Objective from '@src/components/Objective'
import Field from '@src/components/Field'
import Services from '@src/Services'

Enzyme.configure({ adapter: new Adapter() })


beforeEach(() => {
  jest.useFakeTimers()
  fetchMock.reset()

  Services.setConfig({
    apiObjectivesCreateUrl: 'http://www.example.com/export-plan/api/objectives/create/',
    apiObjectivesDeleteUrl: 'http://www.example.com/export-plan/api/objectives/delete/',
    apiObjectivesUpdateUrl: 'http://www.example.com/export-plan/api/objectives/update/',
  })

})

afterEach(() => {
  jest.useRealTimers()
})

describe('Objective', () => {
  test('should generate objective form fields from props and prepopulate', () => {

    const dummyFunction = () => {}

    const dummyObjective = {
      description: 'Some text',
      owner: 'Jane Doe',
      planned_reviews: 'Lorem ipsum',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      showSavedMessage: false,
      isLoading: false,
      errors: []
    }

    const wrapper = Enzyme.mount(
      <Objective
        key={0}
        id={0}
        isLoading={dummyObjective.isLoading}
        errors={dummyObjective.errors}
        showSavedMessage={dummyObjective.showSavedMessage}
        data={dummyObjective}
        number={1}
        handleChange={dummyFunction}
        deleteObjective={dummyFunction}/>
    )

    const plannedReviewsField = (
      <Field
        id="planned_reviews_1"
        type="textarea"
        placeholder="Add some text"
        label="Planned reviews"
        name="planned_reviews"
        value={dummyObjective.planned_reviews}
        errors={[]}
        handleChange={wrapper.props.handleChange}
      />
    )

    const descriptionField = (
      <Field
        id="description_1"
        type="textarea"
        placeholder="Add some text"
        label="Description"
        name="description"
        value={dummyObjective.description}
        errors={[]}
        handleChange={wrapper.props.handleChange}
      />
    )

    const ownerField = (
      <Field
        id="owner_1"
        type="textarea"
        placeholder="Add an owner"
        label="Owner"
        name="owner"
        value={dummyObjective.owner}
        errors={[]}
        handleChange={wrapper.props.handleChange}
      />
    )

    const startDateField = (
      <Field
        id="start_date_1"
        type="date"
        label="Start date"
        name="start_date"
        value={dummyObjective.start_date}
        errors={[]}
        handleChange={wrapper.props.handleChange}
      />
    )

    const endDateField = (
      <Field
        id="end_date_1"
        type="date"
        label="End date"
        name="end_date"
        value={dummyObjective.end_date}
        errors={[]}
        handleChange={wrapper.props.handleChange}
      />
    )

    expect(wrapper.containsMatchingElement(descriptionField)).toEqual(true)
    expect(wrapper.containsMatchingElement(plannedReviewsField)).toEqual(true)
    expect(wrapper.containsMatchingElement(ownerField)).toEqual(true)
    expect(wrapper.containsMatchingElement(startDateField)).toEqual(true)
    expect(wrapper.containsMatchingElement(endDateField)).toEqual(true)
  })


})
