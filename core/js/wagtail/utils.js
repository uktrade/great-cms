export const isAddVideoPage = (pathname) => pathname === '/admin/media/video/add/';

export const showHideElements = (show, hide) => {
    document.querySelector(show).style.display = 'block';
    document.querySelector(hide).style.display = 'none';
}

export const createElement = (el, options=[]) => {
    const _el = document.createElement(el);

    if (_el) {
        options.forEach(({key, val}) => {
            _el[key] = val;
        });

        return _el;
    }

    return document.createElement('div');
}
