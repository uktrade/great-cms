import { decorate } from '@storybook/addon-actions'
import { withKnobs, select } from '@storybook/addon-knobs'
import { backgrounds } from '../../../.storybook/config'
import './spinner'

const decoratedAction = decorate([() => ['Click']])

export default {
    title: 'Spinner',
    parameters: {
        decorators: [withKnobs],
        'in-dsm': {
            docFilePath: './spinner.docs.json',
            containerClass: 'sample-code',
            id: '<DSM component container ID>',
        },
    },
}

const availableThemes = {
    light: 'light',
    dark: 'dark',
}
const availableSizes = {
    sm: 'sm',
    lg: 'lg',
}

export const Dark = () => {
    const theme = select('theme', availableThemes, availableThemes.dark)
    const size = select('size', availableSizes, availableSizes.lg)

    return decoratedAction.withActions({ 'click great-spinner': 'Great spinner clicked' })(
        () =>
            ` <div class="sample-code">
            <great-spinner size="${size}" theme="${theme}"></great-spinner>
        </div>`
    )
}

export const Light = () => {
    const theme = select('theme', availableThemes, availableThemes.light)
    const size = select('size', availableSizes, availableSizes.lg)

    return decoratedAction.withActions({ 'click great-spinner': 'Great spinner clicked' })(
        () =>
            ` <div class="sample-code">
              <great-spinner size="${size}" theme="${theme}"></great-spinner>
          </div>`
    )
}

Light.story = {
    parameters: {
        backgrounds: [...backgrounds, { name: 'Light Gray', value: '#555555', default: true }],
    },
}
