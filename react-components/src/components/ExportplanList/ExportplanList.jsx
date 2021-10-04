import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom'
import { useSelector, Provider } from 'react-redux'
import Services from '@src/Services'
import ExportplanCard from '@src/components/ExportplanList/ExportplanCard'

export const ExportplanList = () => {
  const [epList, setEpList] = useState([])

  useEffect(() => {
    let isMounted = true

    isMounted &&
      Services.getExportplanList().then((result) => setEpList(result))

    return () => (isMounted = false)
  }, [])

  return (
    <div className="bg-blue-deep-10">
      <div className="container p-v-s">
        <nav>
          <ul>
            {epList.map((card) => (
              <ExportplanCard key={card.pk} {...card} />
            ))}
          </ul>
        </nav>
      </div>
    </div>
  )
}

export default function createExportplanList({ element }) {
  ReactDOM.render(
    <Provider store={Services.store}>
      <ExportplanList />
    </Provider>,
    element
  )
}
