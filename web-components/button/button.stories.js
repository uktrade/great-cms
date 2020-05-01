import { decorate } from '@storybook/addon-actions';
import { withKnobs, select, text, boolean } from '@storybook/addon-knobs';
import buttonDocs from './button.mdx';
import { Button } from './button';


customElements.define('great-button', Button);
const decoratedAction = decorate([() => ['Click']]);

export default {
  title: 'Great Button',
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

export const primary  = () => {
  const icon = select('icon', availableIcons, availableIcons.none);
  const disabled = boolean('disabled', false);
  const children = text('text', 'Simple Button');
  return decoratedAction.withActions({ 'click dsm-button': 'Native button clicked!' })(
    () =>
    `<div class="gds-container">
        <great-button icon="${icon}" ${disabled ? 'disabled' : ''}>${children}</great-button>
     </div>
      `
  );
};

primary.story = {
  parameters: {
    // Story-Level 'in-dsm' configuration (Will apply only to the story that is being configured)
    // Story-Level configuration will override Module-Level 'in-dsm' configuration for the specific story
    'in-dsm': {
      docFilePath: './button.docs.json',
      containerClass: 'container'
    },
    docs: { page: buttonDocs }
  }
};