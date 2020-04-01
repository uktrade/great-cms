import ComponentService from '@src/services/components.service.js';

describe('Component service', () => {
    const element = document.createElement('div');
    const secondElement = document.createElement('span');
    class RandomComponent { };
    class SecondRandomComponent { };

    beforeEach(() => {
        ComponentService.addInitialisedComponent(RandomComponent.name, element);
    });

    afterEach(() => {
        ComponentService.removeAllInitialisedComponents();
    });

    test('addInitialisedComponent to add component to the array', () => {
        ComponentService.addInitialisedComponent(RandomComponent.name, secondElement);
        expect(ComponentService.getInitialisedComponents()).toEqual({ "RandomComponent": [element, secondElement] });
    });

    test('addInitialisedComponent to add a second component to the array', () => {
        ComponentService.addInitialisedComponent(SecondRandomComponent.name, secondElement);
        expect(ComponentService.getInitialisedComponents()).toEqual({ "RandomComponent": [element], "SecondRandomComponent": [secondElement] });
    });

    test('getInitialisedComponent to retrieve the component from the array', () => {
        ComponentService.removeInitialisedComponents('RandomComponent');
        expect(ComponentService.getInitialisedComponents()).toEqual({ "RandomComponent": [] });
    });

    test('removeInitialisedComponents to remove component from the array', () => {
        ComponentService.addInitialisedComponent(SecondRandomComponent.name, secondElement);
        expect(ComponentService.getInitialisedComponent("SecondRandomComponent")).toEqual([secondElement]);
    });
});