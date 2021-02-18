import React from 'react'
import ReactDOM from 'react-dom'

import { TravelPlanStats } from '@src/components/TravelPlan/TravelPlanStats/TravelPlanStats'
import { PlannedTravel } from '@src/components/TravelPlan/PlannedTravel/PlannedTravel'
import { CultureRules } from '@src/components/TravelPlan/CultureRules/CultureRules'
import { VisaInformation } from '@src/components/TravelPlan/VisaInformation/VisaInformation'

export const travelPlanSnapshot = ({ element, ...params }) => {
  ReactDOM.render(<TravelPlanStats {...params} />, element)
}

export const travelPlanCultureRules = ({ element, ...params }) => {
  ReactDOM.render(<CultureRules {...params} />, element)
}

export const travelPlanVisaInformation = ({ element, ...params }) => {
  ReactDOM.render(<VisaInformation {...params} />, element)
}

export const plannedTravel = ({ element, ...params }) => {
  ReactDOM.render(<PlannedTravel {...params} />, element)
}
