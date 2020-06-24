import { decorate } from '@storybook/addon-actions'
import { withKnobs, select } from '@storybook/addon-knobs'
import availableIcons from '../../utils/availableIcons'
import iconDocs from './icon.mdx'
import './icon'

const decoratedAction = decorate([() => ['Click']])

export default {
    title: 'Icon',
    parameters: {
        docs: { page: iconDocs },
        decorators: [withKnobs],
        'in-dsm': {
            docFilePath: './icon.docs.json',
            containerClass: 'sample-code',
            id: '<DSM component container ID>',
        },
    },
}

const availableSizes = {
    sm: 'sm',
    lg: 'lg',
    xl: 'xl',
    xxl: 'xxl',
}
const availableThemes = {
    primary: 'primary',
    secondary: 'secondary',
}

export const All = () => {
    const size = select('size', availableSizes, availableSizes.lg)
    return decoratedAction.withActions({ 'click great-icon': 'Great icon clicked' })(
        () =>
            `<style>
                .sample-code {display: flex; flex-wrap: wrap; padding: 60px}
                p {font-family: Arial, san-serif;}
                article {text-align: center; padding: 20px; min-width: 160px}
            </style>
            <div class="sample-code">
        ${Object.values(availableIcons)
            .map(
                (name) => `<article>
                <great-icon name="${name}" size="${size}" theme="primary"></great-icon>
                <p>${name}</p>
            </article>`
            )
            .join('')}
      </div>`
    )
}

export const Single = () => {
    const name = select('name', availableIcons, availableIcons.play)
    const size = select('size', availableSizes, availableSizes.lg)
    const theme = select('theme', availableThemes, availableThemes.primary)
    return decoratedAction.withActions({ 'click great-icon': 'Great icon clicked' })(
        () =>
            `<div class="sample-code">
          <great-icon name="${name}" size="${size}" theme="${theme}"></great-icon>
      </div>`
    )
}
