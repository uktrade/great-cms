import React from 'react'
import { mount } from 'enzyme'
import Tooltip from '@src/components/Tooltip/Tooltip';

describe('Tooltip component', () => {
    test('Matches the snapshot', () => {
        const props = {
            tooltipContent: document.createElement('div')
        };

        const wrapper = mount(<Tooltip {...props} />);

        expect(wrapper).toMatchSnapshot();
    });
});
