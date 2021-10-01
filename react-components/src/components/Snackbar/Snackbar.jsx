import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom'
import { useSelector, Provider } from 'react-redux'
import Services from '@src/Services'
import actions from '@src/actions'

const fadeDelay = 3000

export const Snackbar = () => {
  const notifications = useSelector((state) => state && state.snackbar) || {}
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
      setTimeout(() => fadeStart(newMaxKey), fadeDelay)
      setMaxKey(newMaxKey)
    }
  }, [notifications])
  return (
    <div className="snackbar w-1-2 p-h-s">
      {Object.keys(notifications.queue || {}).map((key) => {
        const notification = notifications.queue[key]
        return (
          <div
            key={key}
            className={`snackbar-message p-h-s p-v-xs m-t-xs bg-blue-deep-80 text-white radius ${
              notification.fade ? 'fade' : ''
            }`}
          >
            {notification.icon && <i className={`fa ${notification.icon} m-r-xs`} />}
            <span>{notification.message}</span>
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
