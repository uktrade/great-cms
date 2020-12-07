import React from 'react'
import { connect, Provider } from 'react-redux'

import Services from '@src/Services'
import { updateField } from '@src/actions/costsAndPricing'
import { CostsAndPricing } from '.'

const mapStateToProps = ({
  exportPlan: { markets },
  costAndPricing
}) => ({
  country: markets.find(Boolean).country_name,
  data: { ...costAndPricing }
})

const mapDispatchToProps = (dispatch) => ({
  update: field => { dispatch(updateField(field)) }
})

const ConnectedContainer = connect(mapStateToProps, mapDispatchToProps)(CostsAndPricing)

export default ({ ...params}) => (
  <Provider store={Services.store}>
    <ConnectedContainer {...params} />
  </Provider>
)
