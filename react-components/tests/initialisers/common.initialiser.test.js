import ComponentInitialiser from '@src/initialisers/common.initialiser.js';
import ComponentService from '@src/services/components.service.js';
import React from 'react';

describe('Component initialiser', () => {
    let initialiser, container;
    class FakeComponent extends React.Component {
        constructor(props) {
            super(props);
        }
        render() { return <div></div> };
    };
    class EmptyFakeComponent extends React.Component {
        constructor(props) {
            super(props);
        }
        render() { return <div></div> };
    };
    const COMPONENTS_CONFIG = [
        {
            name: "FakeComponent",
            props: {
                selector: ".fake-component"
            }
        },
        {
            name: "EmptyFakeComponent",
            props: {
                selector: '.not-present-component'
            }
        }
    ];
    const COMPONENTS = {
        FakeComponent,
        EmptyFakeComponent
    };

    beforeEach(() => {
        container = document.createElement('div');
        container.classList.add('fake-component');
        document.body.appendChild(container);

        initialiser = new ComponentInitialiser();
        initialiser.initialiseComponents(document, COMPONENTS_CONFIG, COMPONENTS);
    });

    afterEach(() => {
        initialiser = null;
        document.body.removeChild(container);
        container = null;
        ComponentService.removeAllInitialisedComponents();
    });

    test('initialiser loads components and their dom instances', () => {
        expect(ComponentService.getInitialisedComponents()).toEqual({ "EmptyFakeComponent": [], "FakeComponent": [container] });
    });

    test('initialiser loads additional component with corresponding dom instance', () => {
        let newContainer = document.createElement('div');
        newContainer.classList.add('not-present-component');
        document.body.appendChild(newContainer);

        initialiser.initialiseComponents(document, COMPONENTS_CONFIG, COMPONENTS);

        expect(ComponentService.getInitialisedComponents()).toEqual({ "EmptyFakeComponent": [newContainer], "FakeComponent": [container] });
    });
});