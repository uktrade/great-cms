import { useEffect } from 'react'

export const useNoScroll = (show) => {

  useEffect(() => {
    if (show) {
      document.body.classList.add('no-scoll')
    } else {
      document.body.classList.remove('no-scoll')
    }
  }, [show])
}
