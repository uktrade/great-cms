import React from 'react'
import ReactDOM from 'react-dom'

import { TravelPlanStats } from '@src/components/TravelPlan/TravelPlanStats/TravelPlanStats'

export const travelPlanSnapshot = ({ element, ...params }) => {
  ReactDOM.render(<TravelPlanStats {...params} />, element)
}
