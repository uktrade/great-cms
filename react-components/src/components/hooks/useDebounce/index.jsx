import { useCallback, useEffect } from 'react'

const waitTime = 2000

export const useDebounce = (func, wait = waitTime) => {
  let timeout
  let unmounted = false

  useEffect(() => {
    return () => {
      unmounted = true
    }
  }, [])

  return useCallback((...args) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      timeout = null
      if (!unmounted) {
        func(...args)
      }
    }, wait)
  }, [])
}

export const debounce = (func, wait = waitTime) => {
  let timeout
  return (...args) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      timeout = null
      func(...args)
    }, wait)
  }
}
