import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

import { RouteToMarketSection } from '@src/views/sections/MarketingApproach/RouteToMarket/RouteToMarketSection'
import { addItemToList } from '@src/Helpers'
import Services from '../../../../Services'

import './RouteToMarket.scss'

export const RouteToMarket = ({
  field,
  formData
}) => {

  const [rows, setRows] = useState([])
  const [data, setData] = useState([])

  const addTable = () => {
    setRows([
        ...rows,
        rows.length+1
      ]
    )
  }

  useEffect(() => {
    if (data.length > 0) {
      Services.updateExportPlan({
        [field]: data
      })
        .then(() => {})
        .catch(() => {})
    }
  }, [data])

  const update = (i, x) => {
    setData(addItemToList(data, i, x))
  }

  return (
    <>
      {rows.length >=1 && rows.map((i) => RouteToMarketSection(formData, update, i))}
      <div className='button--plus'>
        <span className='icon--plus' />
        <button type='button' onClick={addTable} className='button--stone'>Add route to market</button>
      </div>
    </>
  )
}

RouteToMarket.propTypes = {
  field: PropTypes.string.isRequired,
  formData: PropTypes.shape({
    data:PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string,
        label: PropTypes.string,
        options: PropTypes.arrayOf(PropTypes.string)
      }).isRequired
    ).isRequired,
    example: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired
  }).isRequired
}
