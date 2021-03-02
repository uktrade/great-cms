import { useEffect, useRef } from 'react'

export const useOnOutsideClick = (outsideClick, isOpen) => {
  const element = useRef()

  const onClick = (event) => {
    if (
      !event.target.classList.contains('button--toggle') &&
      element.current &&
      !element.current.contains(event.target)
    ) {
      outsideClick(false)
    } else if (
      event.target.classList.contains('button--toggle') &&
      !event.target.classList.contains('button--toggled')
    ) {
      if (isOpen) {
        outsideClick(false)
      }
    }
  }

  useEffect(() => {
    document.addEventListener('click', onClick, true)
    return () => {
      document.removeEventListener('click', onClick, true)
    }
  }, [outsideClick, element])

  return [element]
}
