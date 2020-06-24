import '@storybook/addon-knobs/register';
import '@storybook/addon-a11y/register';
import '@storybook/addon-backgrounds/register';
import '@storybook/addon-actions/register';
import '@storybook/addon-viewport/register';
import '@storybook/addon-storysource/register';
import { registerDsm } from '@invisionapp/dsm-storybook/register';

registerDsm(process.env.STORYBOOK_DSM);
