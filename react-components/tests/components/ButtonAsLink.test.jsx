import React from 'react'
import { shallow } from 'enzyme'
import ButtonAsLink from '@src/components/ButtonAsLink'

describe('ButtonAsLink component', () => {
    test('should render proper markup', () => {
        const wrapper = shallow(<ButtonAsLink location="moon">Click here</ButtonAsLink>);
        expect(wrapper).toMatchSnapshot();
    })
})
