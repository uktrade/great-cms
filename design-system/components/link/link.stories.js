import { decorate } from '@storybook/addon-actions'
import { withKnobs, text } from '@storybook/addon-knobs'
import linkDocs from './link.mdx'
import './link.js'

const decoratedAction = decorate([() => ['Click']])

export default {
  title: 'Link',
  parameters: {
    docs: { page: linkDocs },
    decorators: [withKnobs],
    'in-dsm': {
      docFilePath: './link.docs.json',
      containerClass: 'sample-code',
      id: '5eb037a083200fded78dc6fb',
    },
  },
}

export const Showcase = () => {
  const children = text('text', 'Navigation link')
  const href = text('href', '/href')
  return decoratedAction.withActions({ 'click great-link': 'Great link clicked' })(
    () =>
      `<div class="sample-code">
            <great-link href="${href}">${children}</great-link>
        </div>`
  )
}
