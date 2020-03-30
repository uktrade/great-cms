let initialisedComponents = {};

export class ComponentService {
    static addInitialisedComponent(component, element) {
        initialisedComponents[component].push(element)
    }

    static getInitialisedComponent(component) {
        return initialisedComponents[component];
    }

    static removeInitialisedComponents(component) {
        initialisedComponents[component] = [];
    }
}