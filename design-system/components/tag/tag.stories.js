import { decorate } from '@storybook/addon-actions'
import { withKnobs, select, text, boolean } from '@storybook/addon-knobs'
import './tag.js'

const decoratedAction = decorate([() => ['Click']])

const availableThemes = {
  primary: 'primary',
  secondary: 'secondary',
}

export default {
  title: 'Tag',
  parameters: {
    decorators: [withKnobs],
    'in-dsm': {
      docFilePath: './tag.docs.json',
      containerClass: 'sample-code',
      id: '5ea9a3800c1c097d75eed596',
    },
  },
}

export const Showcase = () => {
  return decoratedAction.withActions({ 'click great-tag': 'Great tag clicked' })(
    () =>
      `<div class="sample-code"  style="font-family: 'FSLucas'; font-size: 16px;">
            <great-tag theme="primary"
            >
                Gin
            </great-tag>
            and
            <great-tag theme="primary"
            >
                Geneva
            </great-tag>
        </div>`
  )
}

export const Primary = () => {
  const disabled = boolean('disabled', false)
  const theme = select('theme', availableThemes, availableThemes.primary)
  const children = text('text', 'primary tag')

  return decoratedAction.withActions({ 'click great-tag': 'Great tag clicked' })(
    () =>
      `<div class="sample-code">
            <great-tag
                ${disabled ? 'disabled' : ''}
                aria-hidden="true"
                data-test="great-primary-tag"
                theme="${theme}"
                type="submit"
            >
                ${children}
            </great-tag>
        </div>`
  )
}

export const Secondary = () => {
  const disabled = boolean('disabled', false)
  const theme = select('theme', availableThemes, availableThemes.secondary)
  const children = text('text', 'secondary tag')

  return decoratedAction.withActions({ 'click great-tag': 'Great tag clicked' })(
    () =>
      `<div class="sample-code">
            <great-tag
                ${disabled ? 'disabled' : ''}
                theme="${theme}"
            >
                ${children}
            </great-tag>
        </div>`
  )
}

export const Disabled = () => {
    const disabled = boolean('disabled', true)
    const theme = select('theme', availableThemes, availableThemes.primary)
    const children = text('text', 'disabled tag')
  
    return decoratedAction.withActions({ 'click great-tag': 'Great tag clicked' })(
      () =>
        `<div class="sample-code">
              <great-tag
                  ${disabled ? 'disabled' : ''}
                  theme="${theme}"
              >
                  ${children}
              </great-tag>
          </div>`
    )
  }
