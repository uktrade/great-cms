import React from 'react'

import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetchMock from 'fetch-mock'

import Objective from '@src/components/Objective'
import Field from '@src/components/Field'
import Services from '@src/Services'
import Spinner from '@src/components/Spinner/Spinner'
import ErrorList from '@src/components/ErrorList'

Enzyme.configure({ adapter: new Adapter() })

const dummyFunction = () => {}


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

    const dummyObjective = {
      description: 'Some text',
      owner: 'Jane Doe',
      planned_reviews: 'Lorem ipsum',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
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

  test('should show saved message when objective has been saved', () => {

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      showSavedMessage: true,
      isLoading: false,
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

    expect(wrapper.containsMatchingElement(
      <p id="objective-saved-message">Changes saved.</p>
    )).toEqual(true)

  })

  test('should show spinner when objective loading', () => {

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      showSavedMessage: false,
      isLoading: true,
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

    expect(wrapper.containsMatchingElement(
      <Spinner text="Saving..."/>
    )).toEqual(true)

  })

  test('should show ErrorList when there are errors', () => {

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      errors: {__all__: ['Unexpected error', 'Request timed out']}
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

    expect(wrapper.containsMatchingElement(
      <ErrorList errors={['Unexpected error', 'Request timed out']} />
    )).toEqual(true)

  })

  test('should not show ErrorList when there are no errors', () => {

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      errors: {__all__: []}
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

    expect(wrapper.exists('errorlist')).toEqual(false)

  })

  test('should call function on change', () => {

    const mockFunction = jest.fn()

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      showSavedMessage: false,
      isLoading: false,
      errors: {__all__: []}
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
        handleChange={mockFunction}
        deleteObjective={dummyFunction}/>
    )

    const input = wrapper.find('textarea[name="description"]')

    const dummyEvent = {
      target: {name: 'description', value: 'Lorem ipsum'}
    }

    input.simulate('change', dummyEvent)

    expect(mockFunction).toHaveBeenCalled()

  })

  test('should call function on delete', () => {

    const mockFunction = jest.fn()

    const dummyObjective = {
      description: '',
      owner: '',
      planned_reviews: '',
      start_date: '',
      end_date: '',
      companyexportplan: 1,
      pk: 1,
      showSavedMessage: false,
      isLoading: false,
      errors: {__all__: []}
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
        deleteObjective={mockFunction}/>
    )

    const input = wrapper.find('.button--delete')

    input.simulate('click', {})

    expect(mockFunction).toHaveBeenCalled()

  })


})
