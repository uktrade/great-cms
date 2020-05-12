import { decorate } from '@storybook/addon-actions'
import { withKnobs, select, text } from '@storybook/addon-knobs'
import headerDocs from './header.mdx'
import femaleImage from 'design-system/components/avatar/images/female.png'
import maleImage from 'design-system/components/avatar/images/male.png'
import { backgrounds } from '.storybook/config.js'
import './header.js'

const decoratedAction = decorate([() => ['Click']])

export default {
  title: 'Header',
  parameters: {
    backgrounds: [{ name: 'Light', value: '#ccc', default: true }, ...backgrounds],
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

const availableAvatars = {
  female: femaleImage,
  male: maleImage,
  none: '',
}

export const Showcase = () => {
  const defaultNavigation = `<li slot="navigation">
    <great-link href="/learn" theme="secondary">Learn</great-link>
</li>
<li slot="navigation">
    <great-link href="/export-plan" theme="primary">Export plan</great-link>
</li>
<li slot="navigation">
    <great-link href="/markets" theme="primary">Markets</great-link>
</li>
<li slot="navigation">
    <great-link href="/services" theme="primary">Services</great-link>
</li>`
  const navigation = text('navigation', defaultNavigation)
  const parsedNavigation = new DOMParser().parseFromString(navigation, 'text/html').documentElement.textContent
  const avatar = select('avatar', availableAvatars, availableAvatars.female)
  const name = text('name', 'Alex')

  return decoratedAction.withActions({ 'click great-button': 'Great button clicked' })(
    () =>
      `<div class="sample-code">
            <great-header>
                ${parsedNavigation}
                <great-avatar slot="avatar" src="${avatar}"></great-avatar>
                ${name ? `<span slot="name">${name}</span>` : ''}
            </great-header>
        </div>`
  )
}
