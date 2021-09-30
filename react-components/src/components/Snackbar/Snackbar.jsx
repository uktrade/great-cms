import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom'
import { useSelector, Provider } from 'react-redux'
import Services from '@src/Services'
import actions from '@src/actions'

const Snackbar = () => {
  const notifications = useSelector((state) => state.snackbar, {})
  const [maxKey, setMaxKey] = useState(0)

  const cleanUp = (key) => {
    // delete from redux queue
    Services.store.dispatch(actions.popNotification(key, true))
  }

  const fadeStart = (key) => {
    // set fade class to start animation
    setTimeout(() => cleanUp(key), 2000)
    Services.store.dispatch(actions.popNotification(key))
  }

  useEffect(() => {
    const newMaxKey = Object.keys(notifications.queue || {}).reduce(
      (max, key) => (key - 0 > max ? key - 0 : max),
      0
    )
    if (newMaxKey !== maxKey) {
      setTimeout(() => fadeStart(newMaxKey), 3000)
      setMaxKey(newMaxKey)
    }
  }, [notifications])

  return (
    <div className="snackbar">
      {Object.keys(notifications.queue || {}).map((key) => {
        const notification = notifications.queue[key]
        return (
          <div
            key={key}
            className={`p-h-xl p-v-xs m-t-xs bg-blue-deep-80 text-white ${
              notification.fade ? 'fade' : ''
            }`}
          >
            {notification.message}
          </div>
        )
      })}
    </div>
  )
}

export default function createSnackbar({ element }) {
  ReactDOM.render(
    <Provider store={Services.store}>
      <Snackbar />
    </Provider>,
    element
  )
}
