import React from 'react';
import ReactDOM from 'react-dom';
import { act, findRenderedComponentWithType } from 'react-dom/test-utils';

import Modal from 'react-modal';
import renderer from 'react-test-renderer';

import { LoginModal } from '../src/LoginModal';

import {shallow} from 'enzyme';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';


Enzyme.configure({ adapter: new Adapter() });


test('Modal opens on link click', () => {
  const component = shallow(
    <LoginModal action='http://www.example.com' csrfToken='123' />
  );
  component.find('a').simulate('click');

  expect(component.find(Modal).prop('isOpen')).toEqual(true);
});
