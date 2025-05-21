(async function () {
    // Specifies style options to customize the Web Chat canvas.
    // Please visit https://microsoft.github.io/BotFramework-WebChat for customization samples.
    const styleOptions = {
        // Hide upload button.
        hideUploadButton: true,
        typingAnimationDuration: 5000
    };

    try {
        if (!window.WEBCHAT_CONFIG || !window.WEBCHAT_CONFIG.agentUrl) {
            throw new Error('WebChat configuration is missing');
        }

        const tokenEndpointURL = new URL(window.WEBCHAT_CONFIG.agentUrl);
        const locale = document.documentElement.lang || 'en';
        const apiVersion = tokenEndpointURL.searchParams.get('api-version') || '2022-03-01-preview';

        const [directLineURL, token] = await Promise.all([
            fetch(new URL(`/powervirtualagents/regionalchannelsettings?api-version=${apiVersion}`, tokenEndpointURL))
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to retrieve regional channel settings.');
                    }
                    return response.json();
                })
                .then(({ channelUrlsById: { directline } }) => directline),
            fetch(tokenEndpointURL)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to retrieve Direct Line token.');
                    }
                    return response.json();
                })
                .then(({ token }) => token)
        ]);

        // The "token" variable is the credentials for accessing the current conversation.
        // To maintain conversation across page navigation, save and reuse the token.

        // The token could have access to sensitive information about the user.
        // It must be treated like user password.

        const directLine = WebChat.createDirectLine({ domain: new URL('v3/directline', directLineURL), token });

        // Sends "startConversation" event when the connection is established.

        const subscription = directLine.connectionStatus$.subscribe({
            next(value) {
                if (value === 2) {
                    directLine
                        .postActivity({
                            localTimezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                            locale,
                            name: 'startConversation',
                            type: 'event'
                        })
                        .subscribe();

                    // Only send the event once, unsubscribe after the event is sent.
                    subscription.unsubscribe();
                }
            }
        });

        WebChat.renderWebChat({ directLine, locale, styleOptions }, document.getElementById('webchat'));
    } catch (error) {
        console.error('Error initializing WebChat:', error);
        const webchatElement = document.getElementById('webchat');
        if (webchatElement) {
            webchatElement.innerHTML = '<p>Sorry, the chat service is currently unavailable. Please try again later.</p>';
        }
    }
})(); 