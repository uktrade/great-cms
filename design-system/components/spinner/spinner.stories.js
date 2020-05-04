import { decorate } from '@storybook/addon-actions'
import { withKnobs, select, text, boolean } from '@storybook/addon-knobs'
import './spinner.js'

const decoratedAction = decorate([() => ['Click']])

export default {
  title: 'Spinner',
  parameters: {
    // docs: { page: buttonDocs },
    decorators: [withKnobs],
    'in-dsm': {
      docFilePath: './spinner.docs.json',
      containerClass: 'sample-code',
      id: '5cf926dec0f0050ea6ca4a8a',
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
    backgrounds: [
        { name: 'Light', value: '#f8f8fa'},
        { name: 'Dark', value: '#333333', default: true },
    ],
    'in-dsm': {
      docFilePath: './spinner.docs.json',
      containerClass: 'sample-code',
      id: '5cf926dec0f0050ea6ca4a8a',
    },
  },
}
