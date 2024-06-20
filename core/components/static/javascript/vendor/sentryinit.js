/**
 * Return config from meta html elements.
 * @param {string} name - The end part of the meta name attribute.
 * @returns {(string|undefined)}
 */
function config(name) {
  return document.querySelector(`meta[name="intranet:${name}"]`)?.content;
}

function sentryInit() {
  const dsn = config("sentry:dsn");

  if (!dsn) {
    console.log("DSN not provided. Skipping Sentry");
    return;
  }


  Sentry.init({
    dsn,
    release: config("release"),
    environment: config("environment"),
    integrations: [Sentry.browserTracingIntegration(),Sentry.replayIntegration(),],
    tracesSampleRate: Number(config("sentry:browser-traces-sample-rate")),
    replaysSessionSampleRate: Number(config("sentry:browser-traces-sample-rate")),
  });
  console.log("Sentry initialized")
  Sentry.captureMessage("Initialized Sentry", "info");
}

sentryInit();
