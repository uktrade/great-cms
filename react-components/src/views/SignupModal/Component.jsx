import React from 'react'

import { ConnectedContainer as Signup } from '@src/views/Signup/Container'

export default function Component(props){
  const { ...otherProps } = props

  return (
    <Signup {...otherProps} />
  )
}
