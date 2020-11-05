import { useEffect } from 'react'

export const useNoScroll = (show) => {

  useEffect(() => {
    if (show) {
      document.documentElement.classList.add('no-scoll')
    } else {
      document.documentElement.classList.remove('no-scoll')
    }
  }, [show])
}
