import React from 'react';
import ReactDOM from 'react-dom';

import { COMPONENTS_CONFIG } from '../constants/components.config';
import { COMPONENTS } from '../constants/components.const';
import { ComponentService } from '../services/components.service';

export default class ComponentInitialiser {
    constructor() {

        document.addEventListener('DOMContentLoaded', () => {
            this.initialiseComponents(document);
        });

        document.addEventListener('dom-change', (event) => {
            this.initialiseComponents(event.target);
        });
    }

    initialiseComponents(doc) {
        COMPONENTS_CONFIG.forEach((component) => {
            if (!ComponentService.getInitialisedComponent(component.name)) {
                ComponentService.removeInitialisedComponents(component.name)
            }

            Array.from(doc.querySelectorAll(component.props.selector)).forEach(element => {
                if (!ComponentService.getInitialisedComponent(component.name).includes(element)) {
                    const ComponentClass = COMPONENTS[component.name];

                    ComponentService.addInitialisedComponent(component.name, element);
                    ReactDOM.render(<ComponentClass {...component.props} />, element);
                }
            });
        });
    }
}