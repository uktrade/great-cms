import avatar from './avatar.js'
import template from './avatar.html'
import avatarImg from './img/avatar.svg'


export default {
    component: avatar,
    title: 'Avatar',
};

export const Default = () => `${template} <great-avatar src="${avatarImg}"></great-avatar>`;
