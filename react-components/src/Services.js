import { createStore, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'
import { config, setConfig } from '@src/config'

import reducers from '@src/reducers'
import actions from '@src/actions'
import api from '@src/api'

export const store = createStore(reducers, applyMiddleware(thunk))

const setInitialState = (state) => {
  store.dispatch(actions.setInitialState(state))
}

export default { ...api, store, config, setConfig, setInitialState }
