import React from 'react'
import ReactDOM from 'react-dom'

import { AdaptToTargetMarketForm } from '@src/views/sections/AdaptationForYourTargetMarket/adaptToTargetMarketForm'
import { DocumentsForTargetMarketForm } from '@src/views/sections/AdaptationForYourTargetMarket/documentsForTargetMarketForm'

import { Table } from '@src/views/sections/AdaptationForYourTargetMarket/statsForYourTargetMarket'

export const adaptToTargetMarketForm = ({ element, ...params }) => {
  ReactDOM.render(<AdaptToTargetMarketForm {...params} />, element)
}

export const documentsForTargetMarketForm = ({ element, ...params }) => {
  ReactDOM.render(<DocumentsForTargetMarketForm {...params} />, element)
}

export const statsForYourTargetMarket = ({ element, ...params }) => {
  ReactDOM.render(<Table {...params} />, element)
}
