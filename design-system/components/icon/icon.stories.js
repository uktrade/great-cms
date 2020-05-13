import { decorate } from '@storybook/addon-actions'
import { withKnobs, select } from '@storybook/addon-knobs'
import iconDocs from './icon.mdx'
import './icon.js'

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

const availableIcons = {
  arrowDown: 'arrowDown',
  arrowLeft: 'arrowLeft',
  arrowRight: 'arrowRight',
  arrowUp: 'arrowUp',
  close: 'close',
  dots: 'dots',
  heart: 'heart',
  magGlass: 'magGlass',
  menu: 'menu',
  play: 'play',
  plus: 'plus',
  tick: 'tick',
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
      `<div class="sample-code" size="lg">
        ${Object.values(availableIcons)
          .map((name) => `<great-icon name="${name}" size="${size}" theme="primary"></great-icon>`)
          .join('&emsp;&emsp;&emsp;')}
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
