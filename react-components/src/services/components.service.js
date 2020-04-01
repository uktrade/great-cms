let initialisedComponents = {};

export default class ComponentService {
    static addInitialisedComponent(component, element) {
        if (!initialisedComponents[component]) {
            initialisedComponents[component] = [];
        }
        initialisedComponents[component].push(element)
    }

    static getInitialisedComponents() {
        return initialisedComponents;
    }

    static getInitialisedComponent(component) {
        return initialisedComponents[component];
    }

    static removeInitialisedComponents(component) {
        initialisedComponents[component] = [];
    }

    static removeAllInitialisedComponents() {
        initialisedComponents = {};
    }
}