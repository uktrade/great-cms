import { useMemo } from 'react'

let idCounter = 0

const useUniqueId = (prefix) => {
  idCounter += 1
  return `${prefix}-${useMemo(() => idCounter, [prefix])}`
}

export default useUniqueId
