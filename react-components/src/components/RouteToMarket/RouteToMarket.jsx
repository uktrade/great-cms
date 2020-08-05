import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'

import { RouteToMarketSection } from './RouteToMarketSection'
import { addItemToList } from '../../Helpers'
import './RouteToMarket.scss'

const RouteToMarket = (props) => {

  const [rows, setRows] = useState([])
  const [data, setData] = useState([])

  const addTable = () => {
    setRows([
        ...rows,
        rows.length++
      ]
    )
  }

  useEffect(() => {
    if (data.length > 0) console.log('POST DATA HERE',data)
  }, [data])


  const update = (i, x) => {
    setData(addItemToList(data, i, x))
  }

  return (
    <>
      {rows.length >=1 && rows.map((i) => RouteToMarketSection(props, update, i))}
      <div className='button--plus'>
        <span className='icon--plus' />
        <button type='button' onClick={addTable} className='button--stone'>Add route to market</button>
      </div>
    </>
  )
}

function createRouteToMarket({ element, ...params  }) {
  ReactDOM.render(<RouteToMarket {...params} />, element)
}

export { RouteToMarket, createRouteToMarket }
