// static values that will not change during execution of the code
// These are set within the base template
export let config = {}
export const setConfig = function(_config) {
  config = Object.assign(config, _config)
}