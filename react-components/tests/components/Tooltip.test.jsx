import React from 'react'
import { mount } from 'enzyme'
import Tooltip from '@src/components/Tooltip/Tooltip';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

describe('Tooltip component', () => {
    Enzyme.configure({ adapter: new Adapter() })

    test('Matches the snapshot', () => {
        const props = {
            tooltipContent: document.createElement('div')
        };

        const wrapper = mount(<Tooltip {...props} />);

        expect(wrapper).toMatchSnapshot();
    });
});
