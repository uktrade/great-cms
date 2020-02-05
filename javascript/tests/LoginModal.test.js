import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import LoginModal from '../src/LoginModal'
import ErrorList from '../src/ErrorList'

import Services from '../src/Services'


Enzyme.configure({ adapter: new Adapter() })

jest.mock('../src/Services');

const defaultProps = {
  csrfToken: '123',
  handleClose: function () {},
  handleSignupClick: function () {},
  loginUrl: 'http://www.example.com',
  username: '',
  password: '',
}


const createEvent = () => ({ preventDefault: jest.fn() })


beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

test('Modal handles close', () => {
  const event = createEvent()
  const props = {...defaultProps, handleClose: jest.fn()}
  const component = shallow(<LoginModal {...props} />)
  // when the user clicks the close button
  act(() => {
    component.find(Modal).find(".link").simulate('click', event)
  })

  // then the handler is closed
  expect(event.preventDefault).toHaveBeenCalled()
  expect(props.handleClose).toHaveBeenCalled()
})

test('Modal shows error message', () => {
  // when there is an error
  const props = {...defaultProps, errorMessage: 'some error', isOpen: true }
  const component = shallow(<LoginModal {...props} />)
  // then the validation message is displayed
  expect(component.find(ErrorList).prop('message')).toEqual('some error')
})

test('Modal form elements are disabled while in progress', () => {
  // when the form submission is in progress
  const props = {...defaultProps, isOpen: true, isInProgress: true }
  const component = mount(<LoginModal {...props} />)
  // then the form elements are disabled
  expect(component.find('input[name="username"]').getDOMNode().disabled).toEqual(true)
  expect(component.find('input[name="password"]').getDOMNode().disabled).toEqual(true)
  expect(component.find('input[type="submit"]').getDOMNode().disabled).toEqual(true)

})

test('Modal form elements are not disabled while not in progress', () => {
  // when the form submission is in progress
  const props = {...defaultProps, isOpen: true, isInProgress: false }
  const component = mount(<LoginModal {...props} />)
  // then the form elements are disabled
  expect(component.find('input[name="username"]').getDOMNode().disabled).toEqual(false)
  expect(component.find('input[name="password"]').getDOMNode().disabled).toEqual(false)
  expect(component.find('input[type="submit"]').getDOMNode().disabled).toEqual(false)
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
    const event = createEvent()
    Services.checkCredentials.mockImplementation(() => Promise.reject('An erorr occured'));
 
    const props = {...defaultProps, isOpen: true, username: 'username', password: 'password'}
    const component = mount(<LoginModal {...props} />)

    act(() => {
      component.find('form').simulate('submit', event)
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.find(ErrorList).prop('message')).toEqual('An erorr occured')
      expect(window.location.reload).not.toHaveBeenCalled()
      done()
    })
  })

  test('good credentials results in page reload', done => {
    // given the credentials are correct
    const event = createEvent()
    Services.checkCredentials.mockImplementation(() => Promise.resolve());
    const props = {...defaultProps, isOpen: true, username: 'username', password: 'password'}
    const component = mount(<LoginModal {...props} />)

    act(() => {
      component.find('form').simulate('submit', event)
    })

    // then an error message is not displayed
    setImmediate(() => {
      expect(component.find(ErrorList).length).toEqual(0)
      expect(window.location.reload).toHaveBeenCalled()
      done()
    })

  })

})
