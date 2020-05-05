import { decorate } from '@storybook/addon-actions'
import { withKnobs, select } from '@storybook/addon-knobs'
import avatarDocs from './avatar.mdx'
import femaleImage from './images/female.png'
import maleImage from './images/male.png'
import './avatar.js'

const decoratedAction = decorate([() => ['Click']])

export default {
  title: 'Avatar',
  parameters: {
    docs: { page: avatarDocs },
    decorators: [withKnobs],
    'in-dsm': {
      docFilePath: './avatar.docs.json',
      containerClass: 'sample-code',
      id: '5eb02bfbd037c00cc1b2e2fd',
    },
  },
}

const availableImages = {
    female: femaleImage,
    male: maleImage,
    none: '',
  }

export const Showcase = () => {
  return decoratedAction.withActions({ 'click great-avatar': 'Great avatar clicked' })(
    () =>
      `<div class="sample-code">
            <great-avatar src="${availableImages.female}"></great-avatar>
            &emsp;&emsp;&emsp;
            <great-avatar src="${availableImages.male}"></great-avatar>
            &emsp;&emsp;&emsp;
            <great-avatar></great-avatar>
        </div>`
  )
}

export const WithImage = () => {
    const image = select('image', availableImages, availableImages.female)
  
    return decoratedAction.withActions({ 'click great-avatar': 'Great button clicked' })(
      () =>
        `<div class="sample-code">
              <great-avatar src="${image}"></great-avatar>
          </div>`
    )
}

export const EmptyState = () => {
    const image = select('image', availableImages, availableImages.none)
  
    return decoratedAction.withActions({ 'click great-avatar': 'Great button clicked' })(
      () =>
        `<div class="sample-code">
              <great-avatar src="${image}"></great-avatar>
          </div>`
    )
}
