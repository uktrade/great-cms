import { addDecorator, addParameters, configure } from '@storybook/html'
import { withA11y } from '@storybook/addon-a11y'
import centered from '@storybook/addon-centered/html'
import { initDsm } from '@invisionapp/dsm-storybook'
import { INITIAL_VIEWPORTS } from '@storybook/addon-viewport'
import '!style-loader!css-loader!sass-loader!./scss-loader.scss'

/**
 * To override @invisionapp/dsm-storybook custom options\theme you can use Storybook options parameter and theming
 * -- this will only override the specific parameters you change --
 * options: https://github.com/storybooks/storybook/blob/master/docs/src/pages/configurations/options-parameter/index.md
 * theming: https://github.com/storybooks/storybook/blob/master/docs/src/pages/configurations/theming/index.md
 * Example code below
 **/
import { themes } from '@storybook/theming'

export const backgrounds = [
  { name: 'Light', value: '#f8f8fa' },
  { name: 'Dark', value: '#333333' },
  { name: 'Pure Black', value: '#000000' },
  { name: 'Pure White', value: '#ffffff' },
  { name: 'Neutral', value: '#888888' }
]

function setCustomOptions() {
  addParameters({
    options: { theme: { ...themes.light, brandTitle: 'GREAT Design System' } }
  })
}

addParameters({
  backgrounds: [...backgrounds.slice(1), { name: 'Light', value: '#f8f8fa', default: true }]
})
addParameters({ docs: { page: null } })
addDecorator(withA11y)
addDecorator(centered)
addParameters({ viewport: { viewports: INITIAL_VIEWPORTS } })

//Init Dsm
initDsm({
  addDecorator,
  addParameters,
  callback: () => {
    // apply the custom options
    setCustomOptions()
    configure(require.context('../design-system/components', true, /\.stories\.js$/), module)
  }
})
