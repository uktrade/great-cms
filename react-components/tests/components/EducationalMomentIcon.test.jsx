import React from 'react'
import { shallow } from 'enzyme'
import EducationalMomentIcon from '@src/components/EducationalMomentIcon/EducationalMomentIcon';

describe('EducationalMomentIcon component', () => {
    test('Matches the snapshot', () => {
        const wrapper = shallow(<EducationalMomentIcon ariaDescribedBy='' hiddenText=''/>);
        expect(wrapper).toMatchSnapshot();
    });
});
