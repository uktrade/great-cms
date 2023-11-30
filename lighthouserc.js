module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
      startServerCommand: 'DEBUG=False make webserver',
      url: ['http://localhost:8020/'],
      settings: {
        onlyCategories: ['accessibility', 'best-practices', 'seo'],
        skipAudits: ['uses-http2'],
        chromeFlags: '--no-sandbox',
        extraHeaders: JSON.stringify({
          Cookie: 'customCookie=1;foo=bar',
        }),
      },
    },
    assert: {
      assertions: {
        'categories:accessibility': [
          'error',
          { minScore: 0.85, aggregationMethod: 'pessimistic' },
        ],
        'categories:best-practices': [
          'error',
          { minScore: 0.85, aggregationMethod: 'pessimistic' },
        ],
        'categories:seo': [
          'error',
          { minScore: 0.85, aggregationMethod: 'pessimistic' },
        ],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
}
