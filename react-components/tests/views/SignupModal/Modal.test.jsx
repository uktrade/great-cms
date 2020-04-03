import React from 'react'

import { shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import { Base } from '@src/views/SignupModal/Base'
import ModalCentreScreen from '@src/views/SignupModal/ModalCentreScreen'
import ModalHalfScreen from '@src/views/SignupModal/ModalHalfScreen'


Enzyme.configure({ adapter: new Adapter() })


describe('SignupModal', () => {

  test('serves "half" display mode', () => {
    const component = shallow(<Base mode='half' />)

    expect(component.containsMatchingElement(<ModalHalfScreen />)).toBe(true)

  })

  test('serves "centre" display mode', () => {
    const component = shallow(<Base mode='centre' />)

    expect(component.containsMatchingElement(<ModalCentreScreen />)).toBe(true)
  })

})
