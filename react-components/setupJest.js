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

import $ from '../core/components/directory_components/static/directory_components/js/vendor/jquery-3.5.1.min';
global.$ = global.jQuery = $;
