import React from 'react'
import ReactDOM from 'react-dom'

import { FormElements } from '@src/components/FormElements'
import { ObjectivesList } from '@src/components/ObjectivesList'

export const createObjectivesReasons = ({ element, ...params }) => {
  ReactDOM.render(<FormElements {...params} />, element)
}

export const createObjectivesList = ({ element, ...params }) => {
  ReactDOM.render(<ObjectivesList {...params} />, element)
}
