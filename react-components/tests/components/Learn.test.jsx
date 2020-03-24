import React from 'react'
import { shallow } from 'enzyme'
import { Learn } from '@src/components/Learn'

describe('Learn component', () => {
    test('should render proper markup', () => {
        const wrapper = shallow(<Learn />)

        expect(wrapper).toMatchSnapshot()
    })
})
