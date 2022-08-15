import fetchMock from 'fetch-mock'
import '@testing-library/jest-dom'
import 'regenerator-runtime/runtime'

global.fetch = fetchMock

window.matchMedia =
  window.matchMedia ||
  function() {
    return {
      matches: false,
      addListener: function() {},
      removeListener: function() {}
    }
  }

import $ from '../core/components/static/javascript/vendor/jquery-3.6.0.min';
global.$ = global.jQuery = $;
