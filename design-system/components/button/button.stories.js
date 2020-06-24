import { decorate } from '@storybook/addon-actions'
import { withKnobs, select, text, boolean } from '@storybook/addon-knobs'
import availableIcons from '../../utils/availableIcons'
import buttonDocs from './button.mdx'
import './button'

const decoratedAction = decorate([() => ['Click']])
const availableThemes = {
    primary: 'primary',
    secondary: 'secondary',
    tertiary: 'tertiary',
}
const icons = { none: '', ...availableIcons }

export default {
    title: 'Button',
    parameters: {
        docs: { page: buttonDocs },
        decorators: [withKnobs],
        'in-dsm': {
            docFilePath: './button.docs.json',
            containerClass: 'sample-code',
            id: '5ea99ed92fe48e14809d1eec',
        },
    },
}

export const Showcase = () => {
    const buttonText = ['We produce', 'Great', 'Buttons']
    const children = text('text', '')
    const icon = select('icon', icons, icons.none)
    const loading = boolean('loading', false)
    const disabled = boolean('disabled', false)

    return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
        () =>
            `<div class="sample-code">
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="primary"
            >
                ${children || buttonText[0]}
            </great-button>
            &emsp;
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="secondary"
            >
                ${children || buttonText[1]}
            </great-button>
            &emsp;
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="tertiary"
            >
                ${children || buttonText[2]}
            </great-button>
        </div>`
    )
}

export const Primary = () => {
    const children = text('text', 'Primary Button')
    const theme = select('theme', availableThemes, availableThemes.primary)
    const icon = select('icon', icons, icons.none)
    const loading = boolean('loading', false)
    const disabled = boolean('disabled', false)

    return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
        () =>
            `<div class="sample-code">
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="${theme}"
            >
                ${children}
            </great-button>
        </div>`
    )
}

export const Secondary = () => {
    const children = text('text', 'Secondary Button')
    const theme = select('theme', availableThemes, availableThemes.secondary)
    const icon = select('icon', icons, icons.none)
    const loading = boolean('loading', false)
    const disabled = boolean('disabled', false)

    return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
        () =>
            `<div class="sample-code">
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="${theme}"
            >
                ${children}
            </great-button>
        </div>`
    )
}

export const Tertiary = () => {
    const children = text('text', 'Tertiary Button')
    const theme = select('theme', availableThemes, availableThemes.tertiary)
    const icon = select('icon', icons, icons.none)
    const loading = boolean('loading', false)
    const disabled = boolean('disabled', false)

    return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
        () =>
            `<div class="sample-code">
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="${theme}"
            >
                ${children}
            </great-button>
        </div>`
    )
}

export const Disabled = () => {
    const children = text('text', 'Disabled Button')
    const theme = select('theme', availableThemes, availableThemes.primary)
    const icon = select('icon', icons, icons.none)
    const loading = boolean('loading', false)
    const disabled = boolean('disabled', true)

    return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
        () =>
            `<div class="sample-code">
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="${theme}"
            >
            ${children}
            </great-button>
       </div>`
    )
}

export const WithIcon = () => {
    const children = text('text', 'Iconic Button')
    const theme = select('theme', availableThemes, availableThemes.primary)
    const icon = select('icon', icons, icons.play)
    const loading = boolean('loading', false)
    const disabled = boolean('disabled', false)

    return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
        () =>
            `<div class="sample-code">
              <great-button
                  ${disabled ? 'disabled' : ''}
                  ${loading ? 'loading' : ''}
                  icon="${icon}"
                  theme="${theme}"
              >
              ${children}
              </great-button>
         </div>`
    )
}
