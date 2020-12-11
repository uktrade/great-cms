import { useCallback, useEffect } from 'react'

export const useDebounce = (func, wait = 2000) => {
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
