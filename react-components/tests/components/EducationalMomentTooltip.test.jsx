import React from 'react';
import { shallow } from 'enzyme';
import EducationalMomentTooltip from '@src/components/EducationalMomentTooltip';
import EducationalMomentIcon from '@src/components/EducationalMomentIcon/EducationalMomentIcon';

let wrapper;
let fixture = ` <div class="js-hidden educational-moment__tooltip" id="tooltip-id">
                    <h3 class="tooltip__heading h-m">Optional heading</h3>
                    <p class="tooltip__paragraph">First paragraph</p>
                    <p class="tooltip__paragraph">Second paragraph</p>
                </div>`;

let div = document.createElement('div');
div.classList.add('educational-moment');
div.classList.add('educational-moment--tooltip');
div.dataset.tooltipType = 'LEFT';
div.innerHTML = fixture;

const props = {
    id: 'ID',
    heading: 'Heading',
    description: 'Description',
    htmlFixture: div,
    ariaDescribedBy: '',
    hiddenText: ''
};

const iconProps = {
    ariaDescribedBy: '',
    hiddenText: ''
};

describe('EducationalMomentTooltip component', () => {
    beforeEach(() => {
        wrapper = shallow(<EducationalMomentTooltip {...props} />);
    });

    afterEach(() => {
        wrapper = null;
    });

    test('Matches the snapshot', () => {
        expect(wrapper).toMatchSnapshot();
    });

    test('component contains tooltip', () => {
        expect(wrapper.find('.tooltip').exists).toBeTruthy();
    });

    test('component contains EducationalMomentIcon', () => {
        expect(wrapper.find(<EducationalMomentIcon {...iconProps}/>).exists).toBeTruthy();
    });

    test('mouseenter changes displayed state to true', () => {
        expect(wrapper.instance().state.displayed).toBe(false);
        wrapper.simulate('mouseenter', { 'type': 'mouseenter' });
        expect(wrapper.instance().state.displayed).toBe(true);
    });

    test('mouseleave changes displayed state to true', () => {
        wrapper.simulate('mouseenter', { 'type': 'mouseenter' });
        expect(wrapper.instance().state.displayed).toBe(true);
        wrapper.simulate('mouseleave', { 'type': 'mouseleave' });
        expect(wrapper.instance().state.displayed).toBe(false);
    });

    test('onfocus changes displayed state to true', () => {
        expect(wrapper.instance().state.displayed).toBe(false);
        wrapper.simulate('focus');
        expect(wrapper.instance().state.displayed).toBe(true);
    });

    test('blur changes displayed state to false', () => {
        wrapper.simulate('focus');
        expect(wrapper.instance().state.displayed).toBe(true);
        wrapper.simulate('blur');
        expect(wrapper.instance().state.displayed).toBe(false);
    });

    test('pressing ESC closes the tooltip', () => {
        const map = {};
        document.addEventListener = jest.fn((event, cb) => {
            map[event] = cb;
        });

        wrapper = shallow(<EducationalMomentTooltip {...props} />);
        wrapper.simulate('mouseenter', { 'type': 'mouseenter' });
        expect(wrapper.instance().state.displayed).toBe(true);
        map.keydown({ 'keyCode': 27 });
        expect(wrapper.instance().state.displayed).toBe(false);
    });

    test('educational-moment__tooltip element to exist', () => {
        expect(wrapper.find('.educational-moment__tooltip').exists).toBeTruthy();
    });

    test('tooltip__heading element to exist', () => {
        expect(wrapper.find('.tooltip__heading').exists).toBeTruthy();
    });

    test('tooltip__paragraph element to exist', () => {
        expect(wrapper.find('.tooltip__paragraph').exists).toBeTruthy();
    });
});
