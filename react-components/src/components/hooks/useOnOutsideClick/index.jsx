import { useEffect, useRef } from 'react'

export const useOnOutsideClick = (element, outsideClick) => {
  const onClickOrFocus = (event) => {
    if ((element.current && !element.current.contains(event.target)) &&
      (event.target !== document.body) &&
      !event.target.classList.contains('ReactModal__Content'))
      outsideClick(event.target)
  }

  useEffect(() => {
    document.addEventListener('focusin', onClickOrFocus, true)
    document.addEventListener('click', onClickOrFocus, true)
    return () => {
      document.removeEventListener('focusin', onClickOrFocus, true)
      document.removeEventListener('click', onClickOrFocus, true)
    }
  }, [outsideClick, element])
}
