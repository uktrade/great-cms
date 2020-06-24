import { decorate } from '@storybook/addon-actions'
import { withKnobs, select } from '@storybook/addon-knobs'
import logoDocs from './logo.mdx'
import './logo'

const decoratedAction = decorate([() => ['Click']])

export default {
    title: 'Logo',
    parameters: {
        docs: { page: logoDocs },
        decorators: [withKnobs],
        'in-dsm': {
            docFilePath: './logo.docs.json',
            containerClass: 'sample-code',
            id: '5eb02cf7ae9e8941b2d64464',
        },
    },
}

const availableSizes = {
    sm: 'sm',
    lg: 'lg',
}

export const Small = () => {
    const size = select('size', availableSizes, availableSizes.sm)
    return decoratedAction.withActions({ 'click great-logo': 'Great logo clicked' })(
        () =>
            `<div class="sample-code">
            <great-logo size="${size}"></great-logo>
        </div>`
    )
}

export const Large = () => {
    const size = select('size', availableSizes, availableSizes.lg)
    return decoratedAction.withActions({ 'click great-logo': 'Great logo clicked' })(
        () =>
            `<div class="sample-code">
              <great-logo size="${size}"></great-logo>
          </div>`
    )
}
