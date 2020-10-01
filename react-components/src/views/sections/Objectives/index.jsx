import React from 'react'
import ReactDOM from 'react-dom'

import { ObjectivesReasons } from '@src/views/sections/Objectives/ObjectivesReasons'

export const createObjectivesReasons = ({ element, ...params }) => {
  ReactDOM.render(<ObjectivesReasons {...params} />, element)
}
