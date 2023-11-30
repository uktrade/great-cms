module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
      startServerCommand: 'make webserver',
      url: ['http://127.0.0.1:8020'],
      settings: {
        onlyCategories: [
          'performance',
          'accessibility',
          'best-practices',
          'seo',
        ],
        skipAudits: ['uses-http2'],
        chromeFlags: '--no-sandbox',
        extraHeaders: JSON.stringify({
          Cookie: 'customCookie=1;foo=bar',
        }),
      },
    },
    assert: {
      assertions: {
        'categories:performance': [
          'error',
          { minScore: 0.9, aggregationMethod: 'median-run' },
        ],
        'categories:accessibility': [
          'error',
          { minScore: 1, aggregationMethod: 'pessimistic' },
        ],
        'categories:best-practices': [
          'error',
          { minScore: 1, aggregationMethod: 'pessimistic' },
        ],
        'categories:seo': [
          'error',
          { minScore: 1, aggregationMethod: 'pessimistic' },
        ],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
}
