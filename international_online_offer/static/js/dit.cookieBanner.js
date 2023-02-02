dit = window.dit || {}

dit.cookieBanner = new function () {
    this.init = function (options) {
        window.addEventListener('DOMContentLoaded', (function () {
            this.banner = document.getElementById(options.bannerId);
            this.prompt = document.getElementById(options.promptId);
            this.thanks = document.getElementById(options.thanksId);
            this.acceptAll = document.getElementById(options.acceptAllId);
            this.dismiss = document.getElementById(options.dismissId);

            const domainElement = document.getElementById('privacyCookieDomain');

            this.cookieOptions = {
                path: '/',
                domain: domainElement ? domainElement.getAttribute('value') : false,
                secure: window.location.protocol === 'https:',
                days: 365
            }

            this.bindEvents();
        }).bind(this));
    }

    this.buildCookieString = function (name, value, options) {
        if (typeof options === 'undefined') {
            options = {};
        }

        let cookieString = name + '=' + value;

        if (options.path) {
            cookieString += '; path=' + options.path;
        }

        if (options.domain) {
            cookieString += '; domain=' + options.domain;
        }

        if (options.secure) {
            cookieString += '; Secure';
        }

        if (options.days) {
            cookieString += '; max-age=60*60*24*' + options.days;
        }

        return cookieString;
    }

    this.setCookie = function (name, value) {
        document.cookie = this.buildCookieString(name, value, this.cookieOptions);
    }

    this.handleAcceptAll = function () {
        const allPreferences = {"essential": true, "settings": true, "usage": true, "campaigns": true};
        this.setCookie('cookie_preferences_set', 'true');
        this.setCookie('cookies_policy', JSON.stringify(allPreferences));

        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({event: 'cookies_policy_accept'});
        window.dataLayer.push({event: 'gtm.dom'});

        this.prompt.remove();
        this.thanks.style.display = 'block';
    }

    this.handleDismiss = function () {
        this.banner.remove();
    }

    this.bindEvents = function () {
        this.acceptAll.addEventListener('click', this.handleAcceptAll.bind(this));
        this.dismiss.addEventListener('click', this.handleDismiss.bind(this));
    }
}
