/* eslint-disable */
import { createStore } from 'redux'
import { config, setConfig } from '@src/config'

import reducers from '@src/reducers'
import actions from '@src/actions'
import api from '@src/api'

export const store = createStore(reducers)

const setInitialState = function(state) {
  store.dispatch(actions.setInitialState(state))
}

export default Object.assign({},api,{
  store: store,
  config,
  setConfig,
  setInitialState,
})
