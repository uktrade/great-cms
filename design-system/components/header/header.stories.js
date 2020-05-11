import { decorate } from '@storybook/addon-actions'
import { withKnobs } from '@storybook/addon-knobs'
import headerDocs from './header.mdx'
import femaleImage from '../avatar/images/female.png'
import { backgrounds } from '.storybook/config.js'
import './header.js'

const decoratedAction = decorate([() => ['Click']])

export default {
  title: 'Header',
  parameters: {
    backgrounds: [
        { name: 'Light Gray', value: '#555555', default: true },
        ...backgrounds, 
    ],
    centered: { disable: true },
    docs: { page: headerDocs },
    decorators: [withKnobs],
    'in-dsm': {
      docFilePath: './header.docs.json',
      containerClass: 'sample-code',
      id: '5ea99ed92fe48e14809d1eec',
    },
  },
}

export const Showcase = () => {
  return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
    () =>
      `<div class="sample-code">
            <great-header>
                <great-avatar slot="avatar" src="${femaleImage}"></great-avatar>
                <span slot="greeting">Hello Isabella</span>
            </great-header>
        </div>`
  )
}
