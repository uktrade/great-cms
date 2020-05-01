import DefaultStory from './default-story.html';
import template from './banner.html';
import banner from './banner.js';

export default {
    component: banner,
    title: 'Banner',
};

export const Default = () => `${template} ${DefaultStory}`;

export const Advanced = () => `${template} ${DefaultStory}`;
