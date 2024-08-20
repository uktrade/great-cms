module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
      startServerCommand: 'DEBUG=True make webserver',
      url: ['http://localhost:8020/'],
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
          Cookie: 'customCookie=1',
        }),
      },
    },
    assert: {
      assertions: {
        'categories:performance': [
          'error',
          { minScore: 0.45, aggregationMethod: 'pessimistic' },
        ],
        'categories:accessibility': [
          'error',
          { minScore: 0.89, aggregationMethod: 'pessimistic' },
        ],
        'categories:best-practices': [
          'error',
          { minScore: 0.89, aggregationMethod: 'pessimistic' },
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
