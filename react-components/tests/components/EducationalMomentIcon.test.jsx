import React from 'react'
import { shallow } from 'enzyme'
import EducationalMomentIcon from '@src/components/EducationalMomentIcon/EducationalMomentIcon';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

describe('EducationalMomentIcon component', () => {
    Enzyme.configure({ adapter: new Adapter() })

    test('Matches the snapshot', () => {
        const wrapper = shallow(<EducationalMomentIcon />);
        expect(wrapper).toMatchSnapshot();
    });
});
