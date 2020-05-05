import { decorate } from '@storybook/addon-actions'
import { withKnobs } from '@storybook/addon-knobs'
import logoDocs from './logo.mdx'
import './logo.js'

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

export const Small = () => {
  return decoratedAction.withActions({ 'click great-logo': 'Great logo clicked' })(
    () =>
      `<div class="sample-code">
            <great-logo size="sm"></great-logo>
        </div>`
  )
}
