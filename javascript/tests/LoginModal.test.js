import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetchMock from 'fetch-mock'
import "regenerator-runtime/runtime"

import {
  LoginModal,
  checkCredentials,
  MESSAGE_INCORRECT_CREDENTIALS,
  MESSAGE_UNEXPEXCTED_ERROR
} from '../src/LoginModal'

Enzyme.configure({ adapter: new Adapter() })

const formUrl = 'http://www.example.com'
const csrfToken = '123'
const createEvent = () => ({ preventDefault: jest.fn() })


beforeEach(() => {
  fetchMock.reset()
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

test('Modal opens and closes on link click', () => {
  const component = shallow(<LoginModal action={formUrl} csrfToken={csrfToken} />)
  const event = createEvent()

  // when the user clicks the button
  act(() => {
    component.find('a').simulate('click', event)
  })

  // then the modal s open
  expect(component.find(Modal).prop('isOpen')).toEqual(true)
  expect(event.preventDefault).toBeCalled()

  // when the user clicks the close button
  act(() => {
    component.find(Modal).find('button').simulate('click', event)
  })

  // then the modal is closed
  expect(component.find(Modal).prop('isOpen')).toEqual(false)

})

test('Modal shows error message', () => {
  // when there is an error
  const component = shallow(
    <LoginModal action={formUrl} csrfToken={csrfToken} isOpen={true} errorMessage={MESSAGE_UNEXPEXCTED_ERROR} />
  )
  // then the validation message is displayed
  expect(component.find('form div').text()).toEqual(MESSAGE_UNEXPEXCTED_ERROR)
})

test('Modal form elements are disabled while in progress', () => {
  // when the form submission is in progress
  const component = mount(<LoginModal action={formUrl} csrfToken={csrfToken} isOpen={true} isInProgress={true} />)
  // then the form elements are disabled
  expect(component.find('input[name="username"]').getDOMNode().disabled).toEqual(true)
  expect(component.find('input[name="password"]').getDOMNode().disabled).toEqual(true)
  expect(component.find('input[type="submit"]').getDOMNode().disabled).toEqual(true)

})

test('Modal form elements are not disabled while not in progress', () => {
  // when the form submission is in progress
  const component = mount(<LoginModal action={formUrl} csrfToken={csrfToken} isOpen={true} isInProgress={false} />)
  // then the form elements are disabled
  expect(component.find('input[name="username"]').getDOMNode().disabled).toEqual(false)
  expect(component.find('input[name="password"]').getDOMNode().disabled).toEqual(false)
  expect(component.find('input[type="submit"]').getDOMNode().disabled).toEqual(false)

})

test('checkCredentials passes params', done => {
  // given the form submission will result in success.getDOMNodeful login
  fetchMock.post(formUrl, 200)

  checkCredentials({url: formUrl, csrfToken: csrfToken, username: 'example', password: 'password'})

  fetchMock.flush().then(() => {
    const calls = fetchMock.calls()
    expect(calls.length).toEqual(1)
    expect(calls[0][0]).toEqual('http://www.example.com/')
    expect(calls[0][1]).toEqual({
      method: 'post',
      headers: {
       'Accept': 'application/json',
       'Content-Type': 'application/json',
       'X-CSRFToken': '123',
       'X-Requested-With': 'XMLHttpRequest',
      },
      body: '{"username":"example","password":"password"}',
    })
    done()
  })
})


describe('Modal end to end', () => {

  const { reload } = window.location

  beforeEach(() => {
    delete window.location
    window.location = { reload: jest.fn() }
  })

  afterEach(() => {
    window.location.reload = reload
  })

  test('bad credentials results in error message', done => {
    // given the credentials are incorrect
    fetchMock.post(formUrl, 400)
    const event = createEvent()

    const component = mount(<LoginModal action={formUrl} csrfToken={csrfToken} isOpen={true} />)
    // then the validation message is displayed

    act(() => {
      component.find('input[name="username"]').getDOMNode().value = 'username'
      component.find('input[name="password"]').getDOMNode().value = 'password'
      component.find('form').simulate('submit', event)
    })

    fetchMock.flush().then(() => {
      component.update()
      expect(component.find('form div').text()).toEqual(MESSAGE_INCORRECT_CREDENTIALS)
      expect(window.location.reload).not.toHaveBeenCalled()
      done()
    })

  })

  test('server erorr results in error message', done => {
    // given the credentials are incorrect
    fetchMock.post(formUrl, 500)
    const event = createEvent()

    const component = mount(<LoginModal action={formUrl} csrfToken={csrfToken} isOpen={true} />)
    // then the validation message is displayed

    act(() => {
      component.find('input[name="username"]').getDOMNode().value = 'username'
      component.find('input[name="password"]').getDOMNode().value = 'password'
      component.find('form').simulate('submit', event)
    })

    fetchMock.flush().then(() => {
      component.update()
      expect(component.find('form div').text()).toEqual(MESSAGE_UNEXPEXCTED_ERROR)
      expect(window.location.reload).not.toHaveBeenCalled()
      done()
    })

  })

  test('good credentials results in page reload', done => {

    // given the credentials are correct
    fetchMock.post(formUrl, 200)
    const event = createEvent()

    const component = mount(<LoginModal action={formUrl} csrfToken={csrfToken} isOpen={true} />)
    // then the validation message is displayed

    act(() => {
      component.find('input[name="username"]').getDOMNode().value = 'username'
      component.find('input[name="password"]').getDOMNode().value = 'password'
      component.find('form').simulate('submit', event)
    })

    fetchMock.flush().then(() => {
      component.update()
      expect(component.find('form dvv').length).toEqual(0)
      expect(window.location.reload).toHaveBeenCalled()
      done()
    })

  })

})
