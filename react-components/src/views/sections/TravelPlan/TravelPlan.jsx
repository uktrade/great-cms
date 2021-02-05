import React from 'react'
import ReactDOM from 'react-dom'

import { TravelPlanStats } from '@src/components/TravelPlan/TravelPlanStats/TravelPlanStats'
import { PlannedTravel } from '@src/components/TravelPlan/PlannedTravel/PlannedTravel'

export const travelPlanSnapshot = ({ element, ...params }) => {
  ReactDOM.render(<TravelPlanStats {...params} />, element)
}

export const plannedTravel = ({ element, ...params }) => {
  // debugger
  ReactDOM.render(<PlannedTravel {...params} />, element)
}
