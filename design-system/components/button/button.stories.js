import { action, decorate } from '@storybook/addon-actions';
import { withKnobs, select, text, boolean } from '@storybook/addon-knobs';
import buttonDocs from './button.mdx';
import { Button } from './button';

customElements.define('great-button', Button);
const decoratedAction = decorate([() => ['Click']]);

export default {
  title: 'Button',
  parameters: {
    decorators: [withKnobs],
    // Module-Level 'in-dsm' configuration (Will apply to all stories inside the module)
    'in-dsm': { id: '5cf926dec0f0050ea6ca4a8a' }
  }
};

const availableIcons = {
  none: '',
  'chevron-right': 'chevron-right'
};

const availableThemes = {
    primary: 'primary',
    secondary: 'secondary',
    tertiary: 'tertiary',
}

export const Default = () => {
  const icon = select('icon', availableIcons, availableIcons.none);
  const disabled = boolean('disabled', false);
  const loading = boolean('loading', false);
  const theme = select('theme', availableThemes, availableThemes.primary);
  const children = text('text', 'Great Button');
  return decoratedAction.withActions({ 'click dsm-button': 'Native button clicked!' })(
    () =>
    `<div class="gds-container">
        <great-button onClick="${action('button-click')}" ${disabled ? 'disabled' : ''} ${loading ? 'loading' : ''} icon="${icon}" theme="${theme}">${children}</great-button>
     </div>
      `
  );
};

Default.story = {
  parameters: {
    // Story-Level 'in-dsm' configuration (Will apply only to the story that is being configured)
    // Story-Level configuration will override Module-Level 'in-dsm' configuration for the specific story
    'in-dsm': {
      docFilePath: './button.docs.json',
      containerClass: 'container'
    },
    info: { inline: true },
    docs: { page: buttonDocs }
  }
};
 