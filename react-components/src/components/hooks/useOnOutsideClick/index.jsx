import { useEffect, useRef } from 'react'

export const useOnOutsideClick = (outsideClick) => {
  const element = useRef()

  const onClick = (event) => {
    if (element.current && !element.current.contains(event.target)) {
      outsideClick()
      event.stopPropagation()
    }
  }

  useEffect(() => {

    document.addEventListener('click', onClick, true)
    return () => {
      document.removeEventListener('click', onClick, true)
    }
  }, [outsideClick, element])

  return [ element ]
}
