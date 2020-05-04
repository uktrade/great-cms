import { decorate } from '@storybook/addon-actions'
import { withKnobs, select, text, boolean } from '@storybook/addon-knobs'
import buttonDocs from './button.mdx'
import './button.js'

const decoratedAction = decorate([() => ['Click']])
const availableIcons = {
  none: '',
  'chevron-right': 'chevron-right',
}

const availableThemes = {
  primary: 'primary',
  secondary: 'secondary',
  tertiary: 'tertiary',
}

export default {
  title: 'Button',
  parameters: {
    docs: { page: buttonDocs },
    decorators: [withKnobs],
    'in-dsm': {
      docFilePath: './button.docs.json',
      containerClass: 'sample-code',
      id: '5cf926dec0f0050ea6ca4a8a',
    },
  },
}

export const Default = () => {
  const icon = select('icon', availableIcons, availableIcons.none)
  const disabled = boolean('disabled', false)
  const loading = boolean('loading', false)
  const children = text('text', 'Great Button')

  return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
    () =>
      `<div class="sample-code">
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="primary"
            >
                ${children}
            </great-button>
            &nbsp;
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="secondary"
            >
                ${children}
            </great-button>
            &nbsp;
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                icon="${icon}"
                theme="tertiary"
            >
                ${children}
            </great-button>
        </div>`
  )
}

export const Primary = () => {
  const icon = select('icon', availableIcons, availableIcons.none)
  const disabled = boolean('disabled', false)
  const loading = boolean('loading', false)
  const theme = select('theme', availableThemes, availableThemes.primary)
  const children = text('text', 'Primary Button')

  return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
    () =>
      `<div class="sample-code">
            <great-button
                ${disabled ? 'disabled' : ''}
                ${loading ? 'loading' : ''}
                aria-hidden="true"
                data-test="great-button-primary-button"
                icon="${icon}"
                theme="${theme}"
                type="submit"
            >
                ${children}
            </great-button>
        </div>`
  )
}

export const Secondary = () => {
  const icon = select('icon', availableIcons, availableIcons.none)
  const disabled = boolean('disabled', false)
  const loading = boolean('loading', false)
  const theme = select('theme', availableThemes, availableThemes.secondary)
  const children = text('text', 'Secondary Button')

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
  const icon = select('icon', availableIcons, availableIcons.none)
  const disabled = boolean('disabled', false)
  const loading = boolean('loading', false)
  const theme = select('theme', availableThemes, availableThemes.tertiary)
  const children = text('text', 'Tertiary Button')

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
    const icon = select('icon', availableIcons, availableIcons.none)
    const disabled = boolean('disabled', true)
    const loading = boolean('loading', false)
    const theme = select('theme', availableThemes, availableThemes.primary)
    const children = text('text', 'Disabled Button')
  
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
