import React from 'react'
import ReactDOM from 'react-dom'

import { FormWithInputWithExample } from '@src/components/FormWithInputWithExample'
import { ObjectivesList } from '@src/components/ObjectivesList'

export const createObjectivesReasons = ({ element, ...params }) => {
  ReactDOM.render(<FormWithInputWithExample {...params} />, element)
}

export const createObjectivesList = ({ element, ...params }) => {
  ReactDOM.render(<ObjectivesList {...params} />, element)
}
