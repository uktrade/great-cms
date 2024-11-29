// This tagging js is copied from components and now the home for tagging in great-cms
// Polyfill for 'includes' in IE.
if (!String.prototype.includes) {
    String.prototype.includes = function(search, start) {
        if (typeof start !== 'number') {
          start = 0;
        }

        if (start + search.length > this.length) {
          return false;
        } else {
          return this.indexOf(search, start) !== -1;
        }
    }
}


var dit = dit || {}
dit.tagging = dit.tagging || {};
dit.tagging.base = new function() {
    this.init = function(debug_mode) {
        $(document).ready(function() {
            addTaggingForLinks();
            addTaggingForVideos();
            addTaggingForForms();
        });

        function addTaggingForLinks() {
            var leftMouseButton = 0;
            var middleMouseButton = 1;
            $('a')
                .on('mouseup', function(event) {
                    if (event.button === leftMouseButton || event.button === middleMouseButton) {
                        sendLinkEvent($(this));
                    }
                })
                .on('keydown', function(event) {
                    if (event.key === 'Enter') {
                        sendLinkEvent($(this));
                    }
                });
        }

        function addTaggingForVideos() {

            $("#hero-campaign-section-watch-video-button").on('click',function() { sendVideoEvent($(this), 'play') });
            $('video')
                .on('play', function() { sendVideoEvent($(this), 'play') })
                .on('pause', function() { sendVideoEvent($(this), 'pause') })
                .on('ended', function() { sendVideoEvent($(this), 'ended') })
                .on('timeupdate', function() { sendVideoEvent($(this), 'progress') });
        }

        function addTaggingForForms() {
            $('form').on('submit', function() { sendFormEvent($(this)) })
        }

        function sendLinkEvent(link) {
            var action = link.data('ga-action') || 'clickLink';
            var type = link.data('ga-type') || inferLinkType(link);
            var element = link.data('ga-element') || inferElement(link);
            var value = link.data('ga-value') || inferLinkValue(link);
            var destination = link.attr('href');

            sendEvent(linkEvent(action, type, element, value, destination));
        }

        function calculateVideoPercent(video) {
            return Math.floor((video.currentTime / video.duration) * 100);
        }

        function sendVideoEvent(video, action) {
            var videoPercent = 0
            var videoStatus = action
            const currentPercent = calculateVideoPercent(video[0]);
                if (currentPercent < 25)
                    videoPercent = 0;
                else if (currentPercent >= 25 && currentPercent < 50)
                        videoPercent = 25;
                else if (currentPercent >= 50 && currentPercent < 75)
                        videoPercent = 50;
                else if (currentPercent >= 75 && currentPercent < 100)
                        videoPercent = 75;

                else {
                        videoStatus = 'ended'
                        videoPercent = 100
                    }

            var type = video.data('ga-type') || 'video';
            var element = video.data('ga-element') || inferElement(video);
            var value = video.data('ga-value') || inferVideoValue(video);
            var title = video.data('title')
            var videoEvent = event(action, type, element, value)

            if (video.length>0) {
                videoEvent['currentTime'] = video[0].currentTime;
            }
            const eventTitle = document.querySelector('[data-ga-event-title]');
            if (eventTitle) {
                videoEvent['eventTitle'] = eventTitle.getAttribute('data-ga-event-title');
            }
            videoEvent['video_percent'] = videoPercent
            videoEvent['video_title'] = title
            videoEvent['video_status'] = videoStatus
            sendEvent(videoEvent);
        }

        function sendFormEvent(form) {
            var action = form.data('ga-action') || 'submit';
            var type = form.data('ga-type') || 'form';
            var element = form.data('ga-element') || inferElement(form);
            var value = form.data('ga-value') || inferFormValue(form);

            var includeFormData = form.data('ga-include-form-data');
            var formData = includeFormData && includeFormData.toLowerCase() === "true" ? form.serialize() : null;
            var nextUrl = inferNextUrlValue(form);

            sendEvent(formEvent(action, type, element, value, formData, nextUrl));
        }

        function inferLinkType(link) {
            if (isCta(link)) {
                return 'CTA';
            }

            if (isCard(link)) {
                return 'Card';
            }

            return 'PageLink';
        }

        function inferElement(domObject) {
            var sectionTitle = domObject.closest('[data-ga-section]').data('ga-section');
            if (sectionTitle) {
                return sectionTitle;
            }

            var sectionId = domObject.closest('[id]').attr('id');
            if (sectionId) {
                return sectionId;
            }

            return '';
        }

        function inferLinkValue(link) {
            var title = guessTitleFromLinkContents(link);
            if (title) {
                return title;
            }
            return link.text().trim();
        }

        function inferVideoValue(video) {
            return video.find('source').attr('src');
        }

        function inferFormValue(form) {
            return form.attr('action') || '';
        }

        function inferNextUrlValue(form) {
           return form.attr('data-next-url') || '';
        }

        function isCta(link) {
            var ctaClasses = ['button', 'cta'];
            var linkClasses = link.attr('class') || '';
            for (var index=0; index < ctaClasses.length; index++) {
                if (linkClasses.includes(ctaClasses[index])) {
                    return true;
                }
            }
            return false;
        }

        function isCard(link) {
            if (link.text()) {
                return false;
            }

            var cardClasses = ['card'];
            var linkClasses = link.css();
            for (var index=0; index < cardClasses.length; index++) {
                if (linkClasses.includes(cardClasses[index])) {
                    return true;
                }
            }
            return false;
        }

        function guessTitleFromLinkContents(link) {
            var titleElements = ['h1', 'h2', 'h3', 'h4', 'h5', 'span', 'p'];

            for (var index=0; index < titleElements.length; index++) {
                if (link.find(titleElements[index]).text()) {
                    return link.find(titleElements[index]).text().trim();
                }
            }
            return null;
        }

        function event(action, type, element, value) {
            return {
                'event': 'gaEvent',
                'action': action,
                'type': type,
                'element': element,
                'value': value
            }
        }

        function linkEvent(action, type, element, value, destination) {
            var linkEvent = event(action, type, element, value);
            linkEvent['destination'] = destination;

            return linkEvent;
        }

        function formEvent(action, type, element, value, data, nextUrl) {
            var formEvent = event(action, type, element, value);

            if (data) {
                formEvent['formData'] = data;
            }

            if (nextUrl) {
                formEvent['dLV - Next URL'] = nextUrl;
            }

            return formEvent;
        }

        function sendEvent(event) {
            if (debug_mode) {
                console.log(event);
            }

            window.dataLayer.push(event);
        }
    }

};
